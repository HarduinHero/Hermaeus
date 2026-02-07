from argparse import Namespace
from prettytable import prettytable
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import tasks
from enum import Enum
from GuildState import GuildState

from const import BOT_TOKEN, WORKING_DIR

class ActionsName(Enum) :
    INCLUDE = "include"
    EXCLUDE = "exclude"

class CustomClient(discord.Client) :

    user: discord.ClientUser

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        await self.tree.sync()





def main(args=None) -> None :

    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    
    client = CustomClient()

    # Setup /include command
    @client.tree.command(
            name=ActionsName.INCLUDE.value,
            description="Include this channel in the next harvest."
    )
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def slash_include(interaction: discord.Interaction) :
        await interaction.response.defer(ephemeral=True)

        if isinstance(interaction.channel, (discord.ForumChannel, discord.CategoryChannel, discord.DMChannel)) or interaction.channel is None :
            await interaction.edit_original_response(
                content=f":rotating_light: This type of channel is not archivable.")
            return
        
        else :
            if interaction.guild is not None :
                gs = GuildState(interaction.guild.id, interaction.guild.name)
                gs.include_channel(interaction.channel.id, str(interaction.channel.name))
                await interaction.edit_original_response(
                    content=f":green_square: This channel will be harvested.")
            else :
                raise Exception("Normaly imposible state.")
            
    
    # Setup /Exclude command
    @client.tree.command(
            name=ActionsName.EXCLUDE.value,
            description="Exclude this channel from the next harvest."
    )
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def slash_exclude(interaction: discord.Interaction) :
        await interaction.response.defer(ephemeral=True)

        if isinstance(interaction.channel, (discord.ForumChannel, discord.CategoryChannel, discord.DMChannel)) or interaction.channel is None :
            await interaction.edit_original_response(
                content=f":rotating_light: This type of channel is not archivable.")
            return
        else :
            if interaction.guild is not None :
                gs = GuildState(interaction.guild.id, interaction.guild.name)
                gs.exclude_channel(interaction.channel.id)
                await interaction.edit_original_response(
                    content=f":red_square: This channel wont be harvested.")
            else :
                raise Exception("Normaly imposible state.")

        

    
    # Start client
    client.run(BOT_TOKEN)

if __name__ == "__main__" :
   main()
