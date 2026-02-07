from argparse import Namespace
from GuildState import GuildState
from prettytable import PrettyTable
from const import WORKING_DIR, BOT_TOKEN, MESSAGE_ARCHIVE_BATCH_SIZE
from pathlib import Path
import discord
import json
from datetime import datetime
import uuid

def message_to_dict(msg:discord.Message) -> str :
    if isinstance(msg.author, discord.User) :
        author = {
            "id" : msg.author.id,
            "dname" : msg.author.display_name,
            "gname" : msg.author.global_name,
            "is_member" : False,
        }
    else : # Member
        author = {
            "id" : msg.author.id,
            "dname" : msg.author.display_name,
            "gname" : msg.author.global_name,
            "is_member" : True,
        }
     
    if msg.reference is None :
        reference_val = None
    else :
        reference_val = msg.reference.message_id
    
    output = {
        "id"                    : msg.id,
        "author"                : author,
        "content"               : msg.content,
        "mentions"              : {
            "raw_channel_mentions"  : msg.raw_channel_mentions,
            "raw_mentions"          : msg.raw_mentions,
            "raw_role_mentions"     : msg.raw_role_mentions,
        },
        "reference"             : reference_val,
        "created_at"            : msg.created_at.isoformat(),
        "edited_at"             : msg.edited_at.isoformat() if msg.edited_at is not None else None,
        "is_stytem"             : msg.is_system(),
        "system_content"        : msg.system_content if msg.is_system() else "",
        "attachements"          : [
            {"url":A.url, "content_type":A.content_type, "custom_id" : uuid.uuid4().hex} for A in msg.attachments
            ],
        "embeds"                : [
            {"type": em.type, "url" : em.url, "custom_id" : uuid.uuid4().hex} for em in msg.embeds
            ]
    }
    return json.dumps(output)

def process_message_batch(channel_id:int, batch:list[str], harvest_dir:Path, is_last:bool=False) -> None :
    channel_file = harvest_dir / f"channel_msg_{channel_id}.json"
    output = ",\n".join(batch)
    if not(channel_file.exists()) :
        if len(output) > 0 :
            output = "[" + output
        else :
            output = "["
    else :
        output = ",\n" + output
    if is_last :
        if len(output) > 0 :
            output = output + "]"
        else :
            output = "]"


    with channel_file.open("a") as channel_file_fd :
        channel_file_fd.write(output)

def harvest_guild(gs:GuildState) -> None :

    intents = discord.Intents.default()
    client = discord.Client(intents=intents, status=discord.Status.dnd)

    harvest_dir = WORKING_DIR / f"harvest_{gs.guild_id}_{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

    harvest_dir.mkdir(parents=True)

    @client.event
    async def on_ready() :

        for channel_id, channel_name in gs.included_channels :
            print(f"SCRAPING CHANNEL({channel_id}, {channel_name})...", end="")

            channel = client.get_channel(channel_id)
            batch = []
            count = 0

            async for msg in channel.history(limit=None, oldest_first=True) : # type: ignore
                batch.append(message_to_dict(msg))
                count += 1

                if len(batch) == MESSAGE_ARCHIVE_BATCH_SIZE :
                    process_message_batch(int(channel_id), batch, harvest_dir)
                    batch.clear()

            process_message_batch(int(channel_id), batch, harvest_dir, is_last=True)

            print(f"{count} Messages")

        await client.close()


    client.run(BOT_TOKEN)
    print("END")

def list_harvestables() -> None :
    table = PrettyTable(("ID", "Name", "#included channels"))
    table.title = "Harvestable Guilds"
    for gs_path in GuildState.list_guild_states_files() :
        gs = GuildState.from_file(gs_path)
        table.add_row([gs.guild_id, gs.guild_name, len(gs.included_channels)])
    print(table.get_string())

def main(args:Namespace) -> None :
    
    if args.list_harvestables :
        list_harvestables()

    elif args.GUILD_ID is not None :
        harvest_guild(GuildState(args.GUILD_ID))