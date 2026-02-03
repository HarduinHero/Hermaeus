import datetime
import json
import uuid
from collections import namedtuple, defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from discord import (CategoryChannel, DMChannel, ForumChannel, GroupChannel,
                     Interaction, StageChannel, TextChannel, VoiceChannel)

from const import WORKING_DIR

ACTION_DIR = Path(WORKING_DIR) / "actions"


class ActionsName(Enum) :
    MISSING = "missing"
    ARCHIVE = "archive"
    PS      = "ps"

class ActionStatus(Enum) :
    MISSING     = "missing" 
    PENDING     = "Pending"
    RUNNING     = "Running"
    FINISHED    = "Finished"

def actionStatus_to_emoji(status:ActionStatus) -> str :
    match status :
        case ActionStatus.PENDING :
            return ":white_circle:"
        case ActionStatus.RUNNING :
            return ":green_circle:"
        case ActionStatus.FINISHED :
            return ":blue_circle:"
        case _ :
            return ":black_circle:"

class InteractionChannelType(Enum) :
    MISSING             = ("missing",           False)
    DM_CHANNEL          = ("DM Channel",        False)
    GROUP_CHANNEL       = ("Group Channel",     False)
    TEXT_CHANNEL        = ("Text Channel",      True)
    VOICE_CHANNEL       = ("Voice Channel",     True)
    CATEGORY_CHANNEL    = ("Category Channel",  True)
    STAGE_CHANNEL       = ("Stage Channel",     True)
    FORUM_CHANNEL       = ("Forum Channel",     True)

    def __init__(self, channel_type_name, is_guild) -> None:
        super().__init__()
        self.channel_type_name = channel_type_name
        self.is_guild = is_guild
    
def type_to_InteractionChannelType(obj:Any) -> InteractionChannelType :
    return {
        DMChannel       : InteractionChannelType.DM_CHANNEL,
        GroupChannel    : InteractionChannelType.GROUP_CHANNEL,
        TextChannel     : InteractionChannelType.TEXT_CHANNEL,
        VoiceChannel    : InteractionChannelType.VOICE_CHANNEL,
        CategoryChannel : InteractionChannelType.CATEGORY_CHANNEL,
        StageChannel    : InteractionChannelType.STAGE_CHANNEL,
        ForumChannel    : InteractionChannelType.FORUM_CHANNEL,
    }.get(type(obj), InteractionChannelType.MISSING)




class Action :
    
    HistoryItem = namedtuple("HistoryItem", ["timestamp", "event"])

    action_name:ActionsName
    action_status:ActionStatus
    action_id:str
    history:list[HistoryItem]
    interaction_id:int
    interaction_channel_id:int
    interaction_channel_name:str
    interaction_guild_id:Optional[int]
    interaction_guild_name:Optional[str]
    interaction_user_id:int
    interaction_user_name:str
    interaction_channel_type:InteractionChannelType

    @staticmethod
    def load(action_file:Path) -> "Action":
        with action_file.open("r") as action_file_fd :
            action_file_data:dict = json.load(action_file_fd)

        action_obj = Action()

        for attribute_key in action_obj.__dict__.keys() :
            value = action_file_data.get(attribute_key, None)
            action_obj.__dict__[attribute_key] = value

        action_obj.action_name = ActionsName(action_obj.action_name)
        action_obj.action_status = ActionStatus(action_obj.action_status)
        action_obj.interaction_channel_type = InteractionChannelType(*action_obj.interaction_channel_type) # type: ignore

        return action_obj
    
    def save(self) -> None :
        action_file = Path(self.get_filename())

        with action_file.open("w") as action_file_fd :
            json.dump(self.to_json_serializable_dict(), action_file_fd, indent=4)


    def __init__(self, action_name:Optional[ActionsName]=None, interaction:Optional[Interaction]=None) -> None:
        self.action_name                = ActionsName.MISSING
        self.action_status              = ActionStatus.MISSING
        self.action_id                  = uuid.uuid4().hex
        self.history                    = []
        self.interaction_id             = -1
        self.interaction_channel_id     = -1
        self.interaction_channel_name   = ""
        self.interaction_guild_id       = -1
        self.interaction_guild_name     = ""
        self.interaction_user_id        = -1
        self.interaction_user_name      = ""
        self.interaction_channel_type   = InteractionChannelType.MISSING

        if action_name is not None :
            self.action_name = action_name
            self.action_status = ActionStatus.PENDING
            self.history = [
                Action.HistoryItem(datetime.datetime.now().isoformat(), "CREATED")
            ]
        if interaction is not None :
            self.interaction_id = interaction.id
            self.interaction_channel_id = interaction.channel_id # type: ignore
            self.interaction_channel_type = type_to_InteractionChannelType(interaction.channel)
            if isinstance(interaction.channel, DMChannel) :
                self.interaction_channel_name = f"DM:{interaction.channel.recipient}"
            else :
                self.interaction_channel_name = interaction.channel.name # type: ignore

            if interaction.guild is None :
                self.interaction_guild_id   = None
                self.interaction_guild_name = None
            else :
                self.interaction_guild_id = interaction.guild_id
                self.interaction_guild_name = interaction.guild.name

            self.interaction_user_id = interaction.user.id
            self.interaction_user_name = interaction.user.name


    def to_json_serializable_dict(self) -> dict :
        output = self.__dict__.copy()
        output["action_name"]   = self.action_name.value
        output["action_status"] = self.action_status.value
        output["history"]       = self.history.copy()
        output["interaction_channel_type"] = self.interaction_channel_type.value
        return output

    def __repr__(self) -> str:
        return f"Action(d={json.dumps(self.to_json_serializable_dict(), indent=4)}, file={self.get_filename()})"
    
    def __str__(self) -> str:
        return f"Action(action_name={self.action_name}, file={self.get_filename()})"

    def get_filename(self) -> str :
        return (ACTION_DIR / f"act_{self.interaction_user_id}_{self.action_id}.json").as_posix()
            
    
