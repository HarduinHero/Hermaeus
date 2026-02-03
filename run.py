from argparse import Namespace
from action_loop import exec_action
from Action import Action, ActionsName, actionStatus_to_emoji, ACTION_DIR
from prettytable import prettytable
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import tasks

from const import BOT_TOKEN, MESSAGE_ARCHIVE_BATCH_SIZE

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

    # Setup /archive command
    @client.tree.command(
            name=ActionsName.ARCHIVE.value,
            description="Make Hermaeus collect and archive the designated " \
                        "content of the current channel."
    )
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def slash_archive(interaction: discord.Interaction) :
        action = Action(ActionsName.ARCHIVE, interaction)
        action.save()
        channel = interaction.channel
        if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)) or channel is None :
            await interaction.response.send_message(f":rotating_light: cant archive this channel.", silent=True, ephemeral=True, delete_after=30)
            Path(action.get_filename()).unlink()
            return
        
        else :
            await interaction.response.defer(ephemeral=True)
            
            batch = []
            count = 0
            async for message in channel.history(limit=50):
                print([
                    message.id,
                    message.author,
                    message.content,
                    message.embeds,
                    message.reference,
                    message.attachments,
                    message.raw_channel_mentions,
                    message.raw_role_mentions
                    

                ])
                
                batch.append(message)
                if len(batch) == MESSAGE_ARCHIVE_BATCH_SIZE :
                    #save_archive_batch(batch)
                    pass






    # Setup /ps
    @client.tree.command(
            name=ActionsName.PS.value,
            description="Ask Hermaeus a list of what is going on."
    )
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(details="Display all details")
    async def slash_ps(interaction: discord.Interaction, details:bool) :
        await interaction.response.send_message("Responding in DMs.", ephemeral=True, delete_after=5, silent=True)
        msg = ""
        for action_file in ACTION_DIR.iterdir() :
            action = Action.load(action_file)
            msg += f"> # [{actionStatus_to_emoji(action.action_status)} {action.action_status.value}] {action.action_name.value}\n"
            if details :
                msg += f"> Channel ID : `{action.interaction_channel_id}` | Channel Type : `{action.interaction_channel_type.value[0]}`\n"

            if action.interaction_channel_type.is_guild :
                msg += f"> In Guild : {action.interaction_guild_name if action.interaction_guild_name != '' else '*Server is private*'}\n"
                msg += f"> https://discord.com/channels/{action.interaction_guild_id}/{action.interaction_channel_id}) | action_id : `{action.action_id}`\n"
                if details :
                    msg += f"> Guild ID : `{action.interaction_guild_id}` | Interaction ID : `{action.interaction_id}`\n"
            else :
                msg += f"> Not in Guild\n"
                msg += f"> https://discord.com/channels/@me/{action.interaction_channel_id} | Action ID : `{action.action_id}`\n"
                if details :
                    msg += f"> Interaction ID : `{action.interaction_id}`\n"
        await interaction.user.send(msg, suppress_embeds=True)
    
    # Start client
    client.run(BOT_TOKEN)

if __name__ == "__main__" :
   main(Namespace(quiet=False))
