import yaml

__CONFIG_FILENAME = "config.yml"

with open(__CONFIG_FILENAME, "r") as config_file :
    CONFIG:dict = yaml.safe_load(config_file)

# Check for mandatory config values
__mandatory_config_values = [
    "application_id", "bot_public_key", "bot_token"
]
for __mandatory_value in __mandatory_config_values :
    if __mandatory_value not in CONFIG :
        raise ValueError(f"wrong config file, expected {__mandatory_value} to exist.")

DISCORD_API_VERSION = 10

COMMANDS_DIRECTORY = "./commands"
WORKING_DIRECTORY  = "./workdir"
GET_GATEWAY_CACHE_FILE  = f"{WORKING_DIRECTORY}/get_gateway.cache"

BOT_NAME = "Hermaeus"

APPLICATION_ID  = CONFIG["application_id"]
BOT_PUBLIC_KEY  = CONFIG["bot_public_key"]
BOT_TOKEN       = CONFIG["bot_token"]

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
URL_GLOBAL_APPLICATION_COMMANDS = URL_API_BASE + f"/applications/{APPLICATION_ID}/commands"
URL_GET_GATEWAY = URL_API_BASE + "/gateway"

URL_GATEWAY_PARAMS = f"/?v={DISCORD_API_VERSION}&encoding=json"