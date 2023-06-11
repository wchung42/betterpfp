import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class Help(commands.Cog):
    """
    PFP Module
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    async def cog_load(self) -> None:
        print('* Help module READY')


#     async def cog_app_command_error(
#             self, 
#             interaction: discord.Interaction, 
#             error: app_commands.AppCommandError
#     ) -> None:
#         error_message: str = '**[ERROR]:** '
#         if isinstance(error, app_commands.MissingPermissions):
#             error_message += f'You are missing `{error.missing_permissions}` permission(s) to use this command in this channel.'
#         elif isinstance(error, app_commands.BotMissingPermissions):
#             error_message += f'I am missing `{error.missing_permissions}` permission(s) to use this command in this channel.'
#         elif isinstance(error, app_commands.CommandOnCooldown):
#             error_message += f'Command is on cooldown. Wait **{error.retry_after:.2f}** seconds.'
#         elif isinstance(error, discord.NotFound):
#             error_message += f'Could not find channel.\n\n{error}'
#         else:
#             error_message += f'{error}'
#         await interaction.response.send_message(error_message, ephemeral=True)


#     # ---------------------------
#     # Help command
#     # ---------------------------
#     @app_commands.command(name='help', description='Info about commands.')
#     @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild.id, i.user.id))
#     #@app_commands.checks.bot_has_permissions(send_messages=True, read_message_history=True)
#     async def help(self, interaction: discord.Interaction) -> None:
        

    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))