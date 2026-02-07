from argparse import Namespace
from const import WORKING_DIR
from prettytable import PrettyTable
from pathlib import Path
from argparse import ArgumentError
from enum import Enum
import json
from collections import namedtuple
from datetime import datetime, timedelta
import requests
from typing import Union
from urllib.parse import urlsplit

class ATTACHEMENT_TYPES(Enum) :

    # From https://en.wikipedia.org/wiki/Media_type
    APPLICATION = "application"
    AUDIO       = "audio"
    IMAGE       = "image"
    MESSAGE     = "message"
    MULTIPART   = "multipart"
    TEXT        = "text"
    VIDEO       = "video"
    FONT        = "font"
    EXAMPLE     = "example"
    MODEL       = "model"
    HAPTICS     = "haptics"
    UNKNOWN     = "unknown"
    
    @classmethod
    def _missing_(cls, value):
        """
        Make ATTACHEMENT_TYPES(x) case-insensitive
        """
        if isinstance(value, str):
            if value == value.lower() :
                return None    
            return cls(value.lower())
        return None



class EMBED_TYPES(Enum) :

    # From https://discord.com/developers/docs/resources/message#embed-object-embed-types
    RICH        = "rich"
    IMAGE       = "image"
    VIDEO       = "video"
    GIFV        = "gifv"
    ARTICLE     = "article"
    LINK        = "link"
    POLL_RESULT = "poll_result"
    UNKNOWN     = "unknown"

    @classmethod
    def _missing_(cls, value):
        """
        Make EMBED_TYPES(x) case-insensitive
        """
        if isinstance(value, str):
            if value == value.lower() :
                return None    
            return cls(value.lower())
        return None



enrichment_item = namedtuple("enrichment_item", ["channel", "url", "type", "custom_id"])



def get_enrichments(target:Path, 
                    targeted_attachement_types:list[ATTACHEMENT_TYPES],
                    targeted_embeds_types: list[EMBED_TYPES]
                ) -> list[enrichment_item]:
    output = []
    for channel_file in target.iterdir() :
        channel_file_name_split = channel_file.name.split("_")
        if channel_file_name_split[0] == "channel" and channel_file_name_split[1] == "msg" :
            channel_id = channel_file_name_split[2]
            with channel_file.open("r") as channel_file_fd :
                channel_data = json.load(channel_file_fd)

            for msg in channel_data :
                if len(msg["attachements"]) > 0:
                    for attachement in msg["attachements"] :
                        if attachement["content_type"] is None :
                            attachement_type = ATTACHEMENT_TYPES.UNKNOWN
                        else :
                            attachement_type = attachement["content_type"].split("/")[0]

                        if ATTACHEMENT_TYPES(attachement_type) in targeted_attachement_types :
                            output.append(enrichment_item(channel_id, attachement["url"], ATTACHEMENT_TYPES(attachement_type), attachement["custom_id"]))

                if len(msg["embeds"]) > 0:
                    for embed in msg["embeds"] :
                        if embed["type"] is None :
                            embed_type = EMBED_TYPES.UNKNOWN
                        else :
                            embed_type = embed["type"]

                        if EMBED_TYPES(embed_type) in targeted_embeds_types :
                            output.append(enrichment_item(channel_id, embed["url"], EMBED_TYPES(embed_type), attachement["custom_id"]))
    return output



def enrich(target:Path,
           targeted_attachement_types:list[ATTACHEMENT_TYPES],
           targeted_embeds_types:list[EMBED_TYPES]
        ) :
    
    enrichements = get_enrichments(target, targeted_attachement_types, targeted_embeds_types)
    total = len(enrichements)

    attachements_dir    = target.joinpath("attachements")
    embeds_dir          = target.joinpath("embeds")
    attachements_dir.mkdir() # At this moint an error on those mkdir is a problem
    embeds_dir.mkdir()
    enrichment_dir_by_type:dict[Union[ATTACHEMENT_TYPES, EMBED_TYPES], Path] = {}
    for attachement_type in targeted_attachement_types :
        attachement_type_dir = attachements_dir.joinpath(attachement_type.value)
        enrichment_dir_by_type[attachement_type] = attachement_type_dir
        attachement_type_dir.mkdir()
    for embed_type in targeted_embeds_types :
        embed_type_dir = embeds_dir.joinpath(embed_type.value)
        enrichment_dir_by_type[attachement_type] = embed_type_dir
        embed_type_dir.mkdir()

    for index, enrichment in enumerate(enrichements) :
        if enrichment.url is None :
            print(f"SKIPPED : NULL URL: {enrichment}")
        
        output_path = enrichment_dir_by_type[enrichment.type].joinpath(f"{enrichment.channel}_{enrichment.custom_id}{Path(urlsplit(enrichment.url).path).suffix}")

        try :
            response = requests.get(enrichment.url, stream=True)
            response.raise_for_status()  # raises error for 4xx/5xx
        except :
            print(response.status_code)
            print(response.headers)
            print(response.raw)
            print(response.content)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        if index % 10 == 0 :
            print(f"Downloaded {index}/{total} : {round((index/total)*100, 2)}%")



def get_enrichables() -> list[Path]:
    output = []
    for file in WORKING_DIR.iterdir() :
        if  file.name.split("_")[0] == "harvest" and \
            file.is_dir() and \
            not((file.joinpath("attachements")).exists()) and \
            not((file.joinpath("embeds")).exists()) and \
            (datetime.now() - datetime.strptime(file.name.split("_")[2], '%Y-%m-%d-%H%M%S')) <= timedelta(hours=23.0) :

            output.append(file)
    return output 



def list_enrichables() :
    enrichables = get_enrichables()
    table = PrettyTable(["INDEX", "GUILD ID", "DATE", "TIME"])
    table.title = "Enrichables Harvests"
    for index, harvest in enumerate(enrichables) :
        harvest_values = harvest.name.split("_")
        table.add_row([
            index,
            harvest_values[1],
            harvest_values[2][:-7],
            ":".join([harvest_values[2][-6::][i*2:(i*2)+2] for i in range(3)])
        ])
    print(table.get_string())



def main(args:Namespace) -> None :

    if args.list_enrichables :
        list_enrichables()

    elif args.TARGET_INDEX is not None :
        enrichables = get_enrichables()
        if args.TARGET_INDEX < 0 or args.TARGET_INDEX >= len(enrichables) :
            print(f"Hermaeus: error: --target/-t {args.TARGET_INDEX}, Incorrect index. Use --list-enrichables/-l to see valid indexes.")
        
        if args.all_attachement :
            targeted_attachement_types = list(ATTACHEMENT_TYPES)
        elif args.ATTACHEMENT_TYPES  is not None :
            targeted_attachement_types = args.ATTACHEMENT_TYPES
        else :
            targeted_attachement_types = []

        if args.all_embeds :
            targeted_embeds_types = list(EMBED_TYPES)
        elif args.EMBED_TYPES is not None :
            targeted_embeds_types = args.EMBED_TYPES
        else :
            targeted_embeds_types = []

        enrich(enrichables[args.TARGET_INDEX], targeted_attachement_types, targeted_embeds_types)



if __name__ == "__main__" :
    pass