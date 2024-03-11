from . import pdictng
from . import utils
import json
import sys
import os.path
import asyncio
import logging
import base64

from typing import Optional, Any, Union
from subprocess import PIPE, Popen
from asyncio.subprocess import create_subprocess_exec
import typing


class SignalDatastore:
    # startup:
    # make sure accounts.json is populated
    # make sure account keystate is populated
    # launch litestream
    # - LITESTREAM_ACCESS_KEY_ID=minioadmin LITESTREAM_SECRET_ACCESS_KEY=minioadmin ./litestreambin replicate -config ./litestream_backup_accounts.yml

    # shutdown:
    # kill signal-cli
    # backup account keystate
    # stop litestream

    # tldr - this runs before signal-cli is launched, and cleans up afterwards
    # if this is unreliable for any reason we may need to monitor the account keystate file / upload it periodically

    def __init__(self, bot_number: typing.Optional[str] = None):
        # if bot_number unknown check sys.argv[1] and if that doesn't work check BOT_NUMBER in secrets file
        # restore accounts.json file (from envvar if needed) - and make directories
        if not bot_number:
            try:
                bot_number = utils.signal_format(sys.argv[1])
                assert bot_number is not None
            except IndexError:
                bot_number = utils.get_secret("BOT_NUMBER")
        logging.debug("bot number: %s", bot_number)
        self.bot_number = bot_number
        self.litestream_path = "./litestreambin"
        self.loop = asyncio.get_event_loop()
        self.client = pdictng.fasterpKVStoreClient()
        self.keystate: Optional[str] = None
        if os.path.exists("state/data/accounts.json"):
            self.accounts_map = json.loads(open("state/data/accounts.json").read())
        else:
            if not os.path.exists("state/data/"):
                os.makedirs("state/data/")
            accounts_json_encoded = os.environ.get("ACCOUNTS_JSON_ENCODED")
            if not accounts_json_encoded:
                raise Exception("No accounts.json and no ACCOUNTS_JSON_ENCODED envar!")
            accounts_json = base64.b64decode(accounts_json_encoded).decode()
            open("state/data/accounts.json", "w").write(accounts_json)
            self.accounts_map = json.loads(accounts_json)
        maybe_account = [
            a
            for a in self.accounts_map.get("accounts")
            if a.get("number").lstrip("+") == bot_number.lstrip("+")
        ]
        if maybe_account:
            self.account = maybe_account[0]
        else:
            raise Exception("Can't find account for your number!")
        if not os.path.exists(f"state/data/{self.account['path']}.d/"):
            os.makedirs(f"state/data/{self.account['path']}.d/")
        self.litestream_database_path = (
            f"state/data/{self.account['path']}.d/account.db"
        )
        self.litestream_replicate_cmd = f"{self.litestream_path} replicate -config ./litestream_backup_accounts.yml".split()
        self.litestream_restore_cmd = f"{self.litestream_path} restore -config ./litestream_backup_accounts.yml {self.litestream_database_path}".split()

    async def restore_litestream(self) -> None:
        """run the command to restore a database from litestream"""
        self.litestream_restore = await create_subprocess_exec(
            *self.litestream_restore_cmd
        )
        await self.litestream_restore.wait()

    async def start_litestream(self) -> str:
        """start the litestream replication process"""
        self.litestream = await create_subprocess_exec(
            *self.litestream_replicate_cmd,
            stdout=PIPE,
        )
        assert self.litestream.stdout
        line = await self.litestream.stdout.readline()
        return line.decode()

    async def stop_litestream(self) -> int:
        self.litestream.terminate()
        return await self.litestream.wait()

    async def periodic_backup(self, tick_seconds: int = 10) -> bool:
        while True and not self.shutting_down:
            await self.async_ensure_backup()
            await asyncio.sleep(tick_seconds)
        # one last time
        await self.async_ensure_backup()
        return True

    def start_periodic_backup(self) -> None:
        self.shutting_down = False
        self.periodic_backup_task = asyncio.get_event_loop().create_task(
            self.periodic_backup()
        )

    async def stop_periodic_backup(self) -> None:
        self.shutting_down = True
        self.periodic_backup_task.cancel()

    async def async_ensure_backup(self) -> Optional[str]:
        """on shutdown: grab the keystate and post it to the persistence backend"""
        self.keystate = open(f"state/data/{self.account.get('path', '')}").read()
        # compare and store
        if (await self.client.get(self.account.get("uuid"))) != self.keystate:
            result = await self.client.post(self.account.get("uuid"), self.keystate)
            logging.debug(f"keystate change detected - backed up: {result}")
            return result
        return None

    async def async_shutdown(self) -> bool:
        await self.stop_periodic_backup()
        return True

    async def async_startup(self) -> None:
        """on startup: fetch keystate from persistence backend, write it out if it doesn't match the existing contents, then restore more keystate from litestream, then start replication"""
        self.keystate = await self.client.get(self.account.get("uuid"))
        if self.keystate and (
            not os.path.exists(f"state/data/{self.account['path']}")
            or self.keystate != open(f"state/data/{self.account['path']}").read()
        ):
            logging.debug("wrote out keystate as it did not exist")
            open(f"state/data/{self.account['path']}", "w").write(self.keystate)
        await self.restore_litestream()
        await asyncio.sleep(1)
        await self.start_litestream()
        asyncio.get_event_loop().call_later(5, self.start_periodic_backup)

    def startup(self) -> None:
        # FIXME
        self.restore_task = asyncio.create_task(self.async_startup())

    def shutdown(self) -> None:
        # FIXME
        self.backup_task = asyncio.create_task(self.async_ensure_backup())

    def wait_finished(self) -> None:
        # FIXME
        pending = asyncio.all_tasks()
        loop = asyncio.get_running_loop()
        loop.run_until_complete(asyncio.gather(*pending))
