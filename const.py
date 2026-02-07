import yaml
from pathlib import Path

__CONFIG_FILENAME = "config.yml"

with open(__CONFIG_FILENAME, "r") as config_file :
    CONFIG:dict = yaml.safe_load(config_file)

WORKING_DIR = Path(CONFIG["working_directory"])
DISCORD_API_VERSION = CONFIG["discord"]["api_version"]
BOT_NAME            = CONFIG["discord"]["application"]["name"]
APPLICATION_ID      = CONFIG["discord"]["application"]["id"]
BOT_PUBLIC_KEY      = CONFIG["discord"]["application"]["public_key"]
BOT_TOKEN           = CONFIG["discord"]["application"]["token"]
MESSAGE_ARCHIVE_BATCH_SIZE = CONFIG["message_archive_batch_size"]


HEADERS = {
    "Content-Type":"application/json",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Connection":"keep-alive",
}

HEADERS_AUTH = {
    **HEADERS,
    "Authorization": f"Bot {BOT_TOKEN}"
}

URL_API_BASE = f"https://discord.com/api/v{DISCORD_API_VERSION}"
