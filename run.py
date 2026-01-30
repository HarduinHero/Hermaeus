import asyncio
import json
from argparse import Namespace
from pathlib import Path

import requests
from websockets.asyncio.client import connect

from const import (GET_GATEWAY_CACHE_FILE, HEADERS, HEADERS_AUTH,
                   URL_GET_GATEWAY, WORKING_DIRECTORY)
from utils import response_content_cleaner



def get_gateway(refresh:bool=False) -> str :
    cache_file = Path(GET_GATEWAY_CACHE_FILE)
    if not(refresh) and cache_file.exists() and cache_file.is_file() :
        with cache_file.open() as cache_file_fd :
            return cache_file_fd.read()
    else :
        try :
            response = requests.get(
                url=URL_GET_GATEWAY,
                headers=HEADERS
            )
        except ConnectionError :
            raise ConnectionError("Something went wrong while fetching geteway endpoint.")
        else :
            gateway_url = json.loads(response_content_cleaner(response.content))["url"]
            with cache_file.open("w") as cache_file_fd :
                cache_file_fd.write(gateway_url)
            return gateway_url

async def hello() :
    async with connect(get_gateway()) as websocket:
        message = await websocket.recv()
        print(message)
    


def main(args:Namespace) -> None :
    Path(WORKING_DIRECTORY).mkdir(parents=True, exist_ok=True)

    asyncio.run(hello())








if __name__ == "__main__" :
   main(Namespace(quiet=False))
