import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import os


# def compile_pfp(pfp: Image, background_path: str) -> Image:
#     transparent_background = Image.new('RGBA', pfp.size, (0, 0, 0, 0))
#     mask = Image.new('RGBA', pfp.size, 0)
#     draw = ImageDraw.Draw(mask)
#     draw.ellipse((10,10,245,245), fill='black', outline=None) # Replace with percentages
#     new_pfp = Image.composite(pfp, transparent_background, mask)
#     background = Image.open(background_path)
#     background.paste(new_pfp, (22, 22), mask=new_pfp) # Replace with percentages
#     return background


def compile_pfp(pfp: Image, background: Image) -> Image:
    transparent_background = Image.new('RGBA', pfp.size, (0, 0, 0, 0))
    mask = Image.new('RGBA', pfp.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((5,5,250,250), fill='black', outline=None) # Replace with percentages
    new_pfp = Image.composite(pfp, transparent_background, mask)
    background.paste(new_pfp, (22, 22), mask=new_pfp) # Replace with percentages
    return background


class OptionButton(discord.ui.Button):
    def __init__(self, label: str, background_image: Image, style: discord.ButtonStyle):
        super().__init__(label=label.capitalize(), style=style)
        self.background_image = background_image
    
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None

        updated_view = self.view
        for child in updated_view.children:
            if isinstance(child, discord.ui.Button):
                if child.label == self.label:
                    child.style = discord.ButtonStyle.primary
                else:
                    child.style = discord.ButtonStyle.success

        # Get user profile picture
        user_asset: discord.Asset = interaction.user.display_avatar.with_size(256)
        data = BytesIO(await user_asset.read())

        # Call compile_pfp
        old_pfp = Image.open(data).convert('RGBA')
        new_pfp = compile_pfp(old_pfp, self.background_image)

        # Change image in embed of interaction
        embed: discord.Embed = interaction.message.embeds[0]
        if embed:
            with BytesIO() as image_binary:
                new_pfp.save(image_binary, 'PNG')
                image_binary.seek(0)
                pfp_file = discord.File(fp=image_binary, filename='pfp.png')
                embed.set_image(url='attachment://pfp.png')
                await interaction.response.edit_message(attachments=[pfp_file], embed=embed, view=updated_view)


class SelectionView(discord.ui.View):
    def __init__(self, bot: commands.Bot, options: list):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(OptionButton(options[0]['label'], options[0]['background_image'], discord.ButtonStyle.primary))
        for option in options[1:]:
            # Create button for each option
            self.add_item(OptionButton(option['label'], option['background_image'], discord.ButtonStyle.success))
    

class PFP(commands.Cog):
    """
    PFP Module
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    async def cog_load(self) -> None:
        print('* PFP module READY')


    async def cog_app_command_error(
            self, 
            interaction: discord.Interaction, 
            error: app_commands.AppCommandError
    ) -> None:
        error_message: str = '**[ERROR]:** '
        if isinstance(error, app_commands.MissingPermissions):
            error_message += f'You are missing `{error.missing_permissions}` permission(s) to use this command in this channel.'
        elif isinstance(error, app_commands.BotMissingPermissions):
            error_message += f'I am missing `{error.missing_permissions}` permission(s) to use this command in this channel.'
        elif isinstance(error, app_commands.CommandOnCooldown):
            error_message += f'Command is on cooldown. Wait **{error.retry_after:.2f}** seconds.'
        elif isinstance(error, discord.NotFound):
            error_message += f'Could not find channel.\n\n{error}'
        else:
            error_message += f'{error}'
        await interaction.response.send_message(error_message, ephemeral=True)


    # ---------------------------
    # Pride pfp command
    # ---------------------------
    @app_commands.command(name='pride', description='Adds pride decoration to your profile picture.')
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild.id, i.user.id))
    @app_commands.checks.bot_has_permissions(send_messages=True, read_message_history=True)
    async def get_tldr(self, interaction: discord.Interaction) -> None:
        # Get user profile picture
        user_asset: discord.Asset = interaction.user.display_avatar.with_size(256)
        data = BytesIO(await user_asset.read())

        # Get backgrounds
        options: list = []
        path: str = './src/resources/pride'
        for file in os.listdir(path):
            if file.endswith('.png'):
                options.append({
                    'label': file[:-4],
                    'background_image': Image.open(f'{path}/{file}') 
                })

        # Compile new image with background
        old_pfp = Image.open(data).convert('RGBA')
        background_image = options[0]['background_image']
        new_pfp = compile_pfp(old_pfp, background_image)

        # Create embed
        embed: discord.Embed = discord.Embed(
            description=f'{interaction.user.mention}',
            color=discord.Color(0xFFD895),
        )
        embed.set_image(url='attachment://pfp.png')
        view: discord.ui.View = SelectionView(self.bot, options)

        # Send image
        with BytesIO() as image_binary:
            new_pfp.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.response.send_message(
                file=discord.File(fp=image_binary, filename='pfp.png'), 
                embed=embed, 
                view=view,
                ephemeral=True
            )


    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PFP(bot))