# the alternative strategy is like, invent an intermediate representation and notation (and visual frontend), or parse Python and hope folks don't use layers of abstraction that one needs runtime introspection to destructure
import ast
import asyncio
import json
import os
import string
import sys
from typing import Any, Optional

from forest import utils
from forest.core import (
    Message,
    QuestionBot,
    Response,
    get_uid,
    is_admin,
    requires_admin,
)
from forest.pdictng import aPersistDict


class GetStr(ast.NodeTransformer):
    source = open(sys.argv[-1]).read()
    dialogs: list[dict[str, Any]] = []

    def get_source(self, node: ast.AST) -> Optional[str]:
        """Get the code fragments that correspond to a provided AST node."""
        return ast.get_source_segment(self.source, node)

    def get_dialog_fragments(self) -> list[dict[str, Any]]:
        """Wrapper function which abstracts over most of the work.
        Returns the generated set of calls to fetch dialog tidbits."""
        node = ast.parse(self.source)
        self.visit(node)
        return self.dialogs

    def visit_Call(self, node: ast.Call) -> None:
        """Visit ast.Call objects, recursively, looking for calls that match
        self.dialog.get(fragment, default), and recording the metadata."""
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        if isinstance(node.func, ast.Attribute):
            # pylint: disable=too-many-boolean-expressions
            if (
                hasattr(node.func, "attr")
                and node.func.attr == "get"
                and getattr(node.func, "value", False)
                and not isinstance(node.func.value, ast.Name)
                and not isinstance(node.func.value, ast.Subscript)
                and getattr(node.func.value, "attr", "") == "dialog"
            ):
                vals = [
                    (
                        c.value
                        if isinstance(c, ast.Constant)
                        else f"(python) `{self.get_source(c)}`"
                    )
                    for c in node.args
                    if c
                ]
                if len(vals) == 2:
                    output_vals = {"key": vals[0], "fallback": vals[1]}
                else:
                    output_vals = {"key": vals[0]}
                self.dialogs += [{"line_number": node.lineno, **output_vals}]


class Dialog(aPersistDict[str]):
    dialog_keys = GetStr().get_dialog_fragments()

    def __init__(self) -> None:
        super().__init__(self, tag="dialog")


class TalkBack(QuestionBot):
    def __init__(self) -> None:
        self.profile_cache: aPersistDict[dict[str, str]] = aPersistDict("profile_cache")
        self.displayname_cache: aPersistDict[str] = aPersistDict("displayname_cache")
        self.displayname_lookup_cache: aPersistDict[str] = aPersistDict(
            "displayname_lookup_cache"
        )
        super().__init__()
        # okay, this now maps the tag (restore key) of each of the above to the instance of the PersistDict class
        self.state = {
            self.__getattribute__(attr).tag: self.__getattribute__(attr)
            for attr in dir(self)
            if isinstance(self.__getattribute__(attr), aPersistDict)
        }

    async def handle_message(self, message: Message) -> Response:
        if message.quoted_text and is_admin(message):
            maybe_displayname = message.quoted_text.split()[0]
            maybe_id = await self.displayname_lookup_cache.get(maybe_displayname)
            if maybe_id:
                await self.send_message(maybe_id, message.full_text)
                return f"Sent reply to {maybe_displayname}!"
        return await super().handle_message(message)

    @requires_admin
    async def do_send(self, msg: Message) -> Response:
        """Send <recipient> <message>
        Sends a message as MOBot."""
        obj = msg.arg1
        param = msg.arg2
        if not is_admin(msg):
            await self.send_message(
                utils.get_secret("ADMIN"), f"Someone just used send:\n {msg}"
            )
        if obj and param:
            if obj in await self.displayname_lookup_cache.keys():
                obj = await self.displayname_lookup_cache.get(obj)
            try:
                result = await self.send_message(obj, param)
                return result
            except Exception as err:  # pylint: disable=broad-except
                return str(err)
        if not obj:
            msg.arg1 = await self.ask_freeform_question(
                msg.uuid, "Who would you like to message?"
            )
        if param and param.strip(string.punctuation).isalnum():
            param = (
                (msg.full_text or "")
                .lstrip("/")
                .replace(f"send {msg.arg1} ", "", 1)
                .replace(f"Send {msg.arg1} ", "", 1)
            )  # thanks mikey :)
        if not param:
            msg.arg2 = await self.ask_freeform_question(
                msg.uuid, "What would you like to say?"
            )
        return await self.do_send(msg)

    async def get_displayname(self, uuid: str) -> str:
        """Retrieves a display name from a UUID, stores in the cache, handles error conditions."""
        uuid = uuid.strip("\u2068\u2069")
        # displayname provided, not uuid or phone
        if uuid.count("-") != 4 and not uuid.startswith("+"):
            uuid = await self.displayname_lookup_cache.get(uuid, uuid)
        # phone number, not uuid provided
        if uuid.startswith("+"):
            uuid = await self.get_uuid_by_phone(uuid) or uuid
        maybe_displayname = await self.displayname_cache.get(uuid)
        if (
            maybe_displayname
            and "ivenName" not in maybe_displayname
            and " " not in maybe_displayname
        ):
            return maybe_displayname
        maybe_user_profile = await self.profile_cache.get(uuid)
        result = await self.signal_rpc_request("listContacts", recipient=uuid)
        user_given = (
            result.blob.get("result", {}).get("profile", {}).get("givenName", "")
        )
        user_given = user_given.replace(" ", "_")
        if uuid and ("+" not in uuid and "-" in uuid):
            user_short = f"{user_given}_{uuid.split('-')[1]}"
        else:
            user_short = user_given + uuid
        # if we were successful in querying the user name
        if user_given:
            await self.displayname_cache.set(uuid, user_short)
            await self.displayname_lookup_cache.set(user_short, uuid)
            return user_short
        else:
            return "NewUser"

    @requires_admin
    async def do_dump(self, _: Message) -> Response:
        """dump
        returns a JSON serialization of current state"""
        return json.dumps(
            {k: v.dict_ for (k, v) in self.state.items() if "tokens" not in k}, indent=2
        )

    @requires_admin
    async def do_set(self, message: Message) -> Response:
        """set
        set [pdict] [key] [value]
        manipulates a key in a specified pdict
        returns the orignal value and the result of the set command"""
        state_location = message.arg1
        key = message.arg2
        value = message.arg3
        first = await self.state.get(state_location).get(key)
        if "tokens" in state_location:
            first = "[REDACTED]"
        return {
            "original_value": first,
            "set_result": await self.state.get(state_location).set(key, value),
        }

    async def talkback(self, msg: Message) -> Response:
        await self.admin(
            f"{await self.get_displayname(msg.uuid)} says: {msg.full_text}"
        )
        return None


class DialogBot(TalkBack):
    def __init__(self) -> None:
        self.dialog = Dialog()
        super().__init__()
        # wait one second for everything to settle, then create a task to check for dialog.json in PWD and load
        self.dialog_load_task = asyncio.get_event_loop().call_later(
            1, lambda: asyncio.create_task(self.finish_init_by_loading())
        )

    async def finish_init_by_loading(self) -> None:
        """Loads dialog from dialog.json in PWD"""
        # wait for dialog init task to complete
        await self.dialog.init_task
        # if dict is still empty
        if not self.dialog.dict_ and os.path.exists("dialog.json"):
            async with self.dialog.rwlock:
                to_load = json.loads(open("dialog.json").read())
                for k, v in to_load.items():
                    # this uploads to the persistence backend
                    await self.dialog._set(k, v)

    @requires_admin
    async def do_dialogset(self, msg: Message) -> Response:
        """Let's do it live.
        Privileged editing of dialog blurbs, because."""
        user = msg.uuid
        fragment_to_set = msg.arg1 or await self.ask_freeform_question(
            user, "What fragment would you like to change?"
        )
        if fragment_to_set in self.TERMINAL_ANSWERS:
            return "OK, nvm"
        blurb = msg.arg2 or await self.ask_freeform_question(
            user, "What dialog would you like to use?"
        )
        if fragment_to_set in self.TERMINAL_ANSWERS:
            return "OK, nvm"
        if old_blurb := await self.dialog.get(fragment_to_set):
            await self.send_message(user, f"overwriting: {old_blurb}")
        await self.dialog.set(fragment_to_set, blurb)
        return "updated blurb!"

    @requires_admin
    async def do_dialogdump(self, msg: Message) -> Response:
        dialog_json = json.dumps(self.dialog.dict_, indent=2)
        sendfilepath = f"/tmp/Dialog_{get_uid()}.json"
        open(sendfilepath, "w").write(dialog_json)
        await self.send_message(
            msg.uuid, f"dialogload {dialog_json}", attachments=[sendfilepath]
        )
        return "You can forward this message to a compatible bot to load the dialog!"

    @requires_admin
    async def do_dialogload(self, msg: Message) -> Response:
        dialog = json.loads(msg.full_text.lstrip("dialogload "))
        unresolved = []
        valid_keys = {dk.get("key") for dk in self.dialog.dialog_keys if "key" in dk}
        for key, value in dialog.items():
            await self.dialog.set(key, value)
            if key not in valid_keys:
                unresolved += [key]
        if unresolved:
            return f"Found some unresolved keys in this load: {unresolved}"
        return "All good!"

    @requires_admin
    async def do_dialog(self, _: Message) -> Response:
        return "\n\n".join(
            [f"{k}: {v}\n------\n" for (k, v) in self.dialog.dict_.items()]
        )

    @requires_admin
    async def do_dialogkeys(self, _: Message) -> Response:
        return "\n\n".join(
            [
                "\n".join([f"{k}: {v}" for (k, v) in dialogkey.items()])
                for dialogkey in self.dialog.dialog_keys
            ]
        )
