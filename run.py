from argparse import Namespace
from action_loop import action_loop, create_action_file
from enums import Actions

import discord
from discord import app_commands

from const import BOT_TOKEN



class CustomClient(discord.Client) :

    user: discord.ClientUser

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        await self.tree.sync()

def main(args:Namespace) -> None :
    
    client = CustomClient()

    @client.tree.command(
            name=Actions.ARCHIVE.value,
            description="Make Hermaeus collect and archive the designated " \
                        "content of the current channel.",
    )
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    async def slash_archive(
        interaction: discord.Interaction,
    ) :
        await interaction.response.send_message("Starting archiving process")
        print(type(interaction.channel))

    client.run(BOT_TOKEN)

    action_loop()






if __name__ == "__main__" :
   main(Namespace(quiet=False))
