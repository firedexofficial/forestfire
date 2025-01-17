#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team
import functools
from pythonjsonlogger import jsonlogger
import logging
import shutil
import os
from pathlib import Path
from typing import Optional, cast, Dict, Any
import phonenumbers as pn
from phonenumbers import NumberParseException
import datetime


def QuietAiohttp(record: logging.LogRecord) -> bool:
    str_msg = str(getattr(record, "msg", ""))
    if "was destroyed but it is pending" in str_msg:
        return False
    if str_msg.startswith("task:") and str_msg.endswith(">"):
        return False
    return True


logger_class = logging.getLoggerClass()

logger = logging.getLogger()
logger.setLevel("DEBUG")


# See example code at https://pypi.org/project/python-json-logger/
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self, log_record: Dict[Any, Any], record: Any, message_dict: Dict[Any, Any]
    ) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


fmt = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
console_handler = logging.StreamHandler()
console_handler.setLevel(
    ((os.getenv("LOGLEVEL") or os.getenv("LOG_LEVEL")) or "DEBUG").upper()
)
console_handler.setFormatter(fmt)
console_handler.addFilter(QuietAiohttp)
logger.addHandler(console_handler)
logging.getLogger("asyncio").setLevel("INFO")

#### Configure Parameters


# edge cases:
# accessing an unset secret loads other variables and potentially overwrites existing ones
def parse_secrets(secrets: str) -> dict[str, str]:
    pairs = [
        line.strip().split("=", 1)
        for line in secrets.split("\n")
        if line and not line.startswith("#")
    ]
    can_be_a_dict = cast(list[tuple[str, str]], pairs)
    return dict(can_be_a_dict)


# to dump: "\n".join(f"{k}={v}" for k, v in secrets.items())


@functools.cache  # don't load the same env more than once
def load_secrets(env: Optional[str] = None, overwrite: bool = False) -> None:
    if not env:
        env = os.environ.get("ENV", "dev")
    try:
        if not os.path.exists(f"{env}_secrets"):
            logging.info("loading values from .env")
            secrets = parse_secrets(open(".env").read())
        else:
            logging.info("loading values from %s_secrets", env)
            secrets = parse_secrets(open(f"{env}_secrets").read())
        if overwrite:
            new_env = secrets
        else:
            # mask loaded secrets with existing env
            new_env = secrets | os.environ
        os.environ.update(new_env)
    except FileNotFoundError:
        pass


secret_cache: Dict[str, str] = {}


# potentially split this into get_flag and get_secret; move all of the flags into fly.toml;
# maybe keep all the tomls and dockerfiles in a separate dir with a deploy script passing --config and --dockerfile explicitly
def get_secret(key: str, env: Optional[str] = None) -> str:
    if key in secret_cache:
        return secret_cache[key]
    try:
        secret = os.environ[key]
    except KeyError:
        load_secrets(env)
        secret = os.environ.get(key) or ""  # fixme
        secret_cache[key] = secret
    if secret.lower() in ("0", "false", "no"):
        return ""
    return secret


## Parameters for easy access and ergonomic use

# local is when neither running on FLY nor running on K8S
LOCAL = (os.getenv("FLY_APP_NAME") is None) and (
    os.getenv("KUBERNETES_SERVICE_PORT") is None
)

ROOT_DIR = get_secret("ROOT_DIR") or "/app" if not LOCAL else "."
SIGNAL = "signal-cli"
RESTORE = get_secret("RESTORE")

maybe_path = get_secret("SIGNAL_PATH")
if maybe_path and Path(maybe_path).exists():
    SIGNAL_PATH = str(Path(maybe_path).absolute())
elif Path(SIGNAL).exists():
    SIGNAL_PATH = str(Path(SIGNAL).absolute())
elif (Path(ROOT_DIR) / SIGNAL).exists():
    SIGNAL_PATH = str((Path(ROOT_DIR) / SIGNAL).absolute())
elif which := shutil.which(SIGNAL):
    SIGNAL_PATH = which
elif os.getenv("ENV") == "test":
    SIGNAL_PATH = SIGNAL  # doesn't matter, just use something
else:
    raise FileNotFoundError(
        f"Couldn't find a {SIGNAL} executable in the working directory, {ROOT_DIR}, or as an executable in PATH "
        f"Install {SIGNAL} or try symlinking {SIGNAL} to the working directory"
    )

#### Configure logging to file

if get_secret("LOGFILES") or not LOCAL:
    handler = logging.FileHandler("debug.log")
    handler.setLevel("DEBUG")
    handler.setFormatter(fmt)
    handler.addFilter(QuietAiohttp)
    logger.addHandler(handler)


def signal_format(raw_number: str) -> Optional[str]:
    try:
        return pn.format_number(pn.parse(raw_number, "US"), pn.PhoneNumberFormat.E164)
    except NumberParseException:
        return None
