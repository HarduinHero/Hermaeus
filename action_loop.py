from discord import Interaction, Client, utils
from const import WORKING_DIRECTORY
from pathlib import Path
import gzip
from Action import Action, ACTION_DIR, ActionsName, ActionStatus

WORKING_DIR  = Path(WORKING_DIRECTORY)
ARCHIVES_DIR = WORKING_DIR / "archives"    

def clean_up() :
    pass

def archive_channel(client:Client, channel_id:int, action_id:str) :
    archive_tmp_file = WORKING_DIR / f"tmp_{action_id}"

    

    print(client.fetch_channel(channel_id))


async def exec_action(client:Client) :


    for action_file in ACTION_DIR.iterdir() :
        action = Action.load(action_file)

        print(action)

        if action.action_name == ActionsName.ARCHIVE :
            action.action_status = ActionStatus.RUNNING
            action.save()

            print(await client.fetch_channel(action.interaction_channel_id))

            #archive_channel(client, action.interaction_channel_id, action.action_id)


