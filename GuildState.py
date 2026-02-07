import datetime
import json
from collections import namedtuple
from pathlib import Path
from const import WORKING_DIR
from typing import Optional

_GUILDSTATE_FILE_PREFIX:str = "guild"
_GUILDSTATE_FILE_SUFIX:str  = ".json"

class GuildState :
    
    IncludedChannelItem = namedtuple("IncludedChannelItem", ["id", "name"])
    HistoryItem = namedtuple("HistoryItem", ["timestamp", "event"])



    guild_id:int
    guild_name:str
    included_channels:set[IncludedChannelItem]
    history:list[HistoryItem]

    @staticmethod
    def list_guild_states_files() -> list[Path]:
        output = []
        for file in WORKING_DIR.iterdir() :
            if  file.stem[0:len(_GUILDSTATE_FILE_PREFIX)] == _GUILDSTATE_FILE_PREFIX and \
                file.suffix == _GUILDSTATE_FILE_SUFIX :
                output.append(file)
        return output
    
    @staticmethod
    def from_file(guild_state_path:Path) -> "GuildState" :
        return GuildState(int(guild_state_path.stem.split('_')[-1]))

    def __init__(self, guild_id:int, guild_name:Optional[str]=None) -> None:
        self.guild_id   = guild_id
        
        if self.get_path().exists() :
            self.__load()
        else :
            if guild_name is None :
                raise AttributeError("Cant create new GuildState without guild_name")
            self.guild_name = guild_name
            self.included_channels  = set()
            self.history            = [GuildState.HistoryItem(datetime.datetime.now().isoformat(), "CREATED")]
            self.__save()

    def __load(self) -> None:
        with self.get_path().open("r") as guild_state_fd :
            guild_state_file_data:dict = json.load(guild_state_fd)

        for attribute_key in GuildState.__annotations__.keys() :
            value = guild_state_file_data.get(attribute_key, None)
            self.__dict__[attribute_key] = value

        self.included_channels = set([GuildState.IncludedChannelItem(item[0], item[1]) for item in self.included_channels])
        self.history = [GuildState.HistoryItem(item[0], item[1]) for item in self.history]
    
    def __save(self) -> None :
        action_file = Path(self.get_path())
        with action_file.open("w") as action_file_fd :
            json.dump(self.to_json_serializable_dict(), action_file_fd, indent=4)

    def to_json_serializable_dict(self) -> dict :
        output = self.__dict__.copy()
        output["included_channels"] = list(self.included_channels)
        output["history"] = self.history.copy()
        return output

    def __repr__(self) -> str:
        return f"GuildState(d={json.dumps(self.to_json_serializable_dict(), indent=4, ensure_ascii=False)}, file={self.get_path()})"
    
    def __str__(self) -> str:
        return f"GuildState(guild_id={self.guild_id}, guild_name={self.guild_name}, file={self.get_path()})"

    def get_path(self) -> Path :
        return (WORKING_DIR / f"{_GUILDSTATE_FILE_PREFIX}_{self.guild_id}{_GUILDSTATE_FILE_SUFIX}")
    
    def include_channel(self, channel_id:int, channel_name:str) -> None :
        before_len = len(self.included_channels)
        item = GuildState.IncludedChannelItem(channel_id, channel_name)
        self.included_channels.add(item)
        if before_len != len(self.included_channels) :
            self.history.append(GuildState.HistoryItem(datetime.datetime.now().isoformat(), f"INCLUDE {item}"))
            self.__save()

    def exclude_channel(self, channel_id:int) -> None :
        item_to_remove = None
        for item in self.included_channels :
            if item.id == channel_id :
                item_to_remove = item
                break
        if item_to_remove is not None :
            self.included_channels.remove(item_to_remove)
            self.history.append(GuildState.HistoryItem(datetime.datetime.now().isoformat(), f"EXCLUDE {item_to_remove}"))
            self.__save()
                
            
    

            
    
