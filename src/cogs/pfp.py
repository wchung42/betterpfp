import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from PIL import Image, ImageDraw, ImageSequence, GifImagePlugin, PngImagePlugin
from io import BytesIO
import os


def process_static_image(pfp: PngImagePlugin.PngImageFile, background: Image) -> PngImagePlugin.PngImageFile:
    transparent_background = Image.new('RGBA', pfp.size, (0, 0, 0, 0))
    mask = Image.new('RGBA', pfp.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((5,5,250,250), fill='black', outline=None) # Replace with percentages
    new_pfp = Image.new('RGBA', background.size)
    masked_pfp = Image.composite(pfp, transparent_background, mask)
    new_pfp.paste(background, (0, 0))
    new_pfp.paste(masked_pfp, (22, 22), mask=masked_pfp)
    return new_pfp


def process_gif(gif: GifImagePlugin.GifImageFile, background: Image) -> list:
    new_pfp_frames = []
    for frame_num in range(gif.n_frames):
        gif.seek(frame_num)
        new_frame: PngImagePlugin.PngImageFile = process_static_image(gif, background)
        new_pfp_frames.append(new_frame)
    return new_pfp_frames


def isGif(img: Image) -> bool:
    frame_count: int = 0
    for _ in ImageSequence.Iterator(img):
        frame_count +=1
        if frame_count > 1:
            return True
    return False


class OptionButton(discord.ui.Button):
    def __init__(self, label: str, author: str, background_image: Image, style: discord.ButtonStyle):
        super().__init__(label=label.capitalize(), style=style)
        self.author = author
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
        old_pfp = Image.open(data)
        is_gif: bool = isGif(old_pfp)
        new_pfp: PngImagePlugin.PngImageFile | list = process_gif(old_pfp, self.background_image) if is_gif else \
                                                        process_static_image(old_pfp, self.background_image)
        
        # Change image in embed of interaction
        embed: discord.Embed = interaction.message.embeds[0]
        extension: str = 'gif' if is_gif else 'png'
        if embed:
            with BytesIO() as image_binary:
                if is_gif:
                    new_pfp[0].save(image_binary, format=extension, save_all=True, append_images=new_pfp[1:], duration=100, loop=0)
                else:
                    new_pfp.save(image_binary, extension.upper())
                image_binary.seek(0)
                pfp_file = discord.File(fp=image_binary, filename=f'pfp.{extension}')
                embed.set_image(url=f'attachment://pfp.{extension}')
                embed.set_footer(text=f'Designed by {self.author}.')
                await interaction.response.edit_message(attachments=[pfp_file], embed=embed, view=updated_view)


class SelectionView(discord.ui.View):
    def __init__(self, bot: commands.Bot, options: list):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(OptionButton(options[0]['label'], options[0]['author'], options[0]['background_image'], discord.ButtonStyle.primary))
        for option in options[1:]:
            # Create button for each option
            self.add_item(OptionButton(option['label'], option['author'], option['background_image'], discord.ButtonStyle.success))
    

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
    #@app_commands.checks.bot_has_permissions(send_messages=True, read_message_history=True)
    async def generate_pride_pfp(self, interaction: discord.Interaction) -> None:
        # Get backgrounds
        options: list = []
        path: str = './src/resources/pride'
        for file in sorted(os.listdir(path)):
            if file.endswith('.png'):
                info: list = file[:-4].split('_')
                options.append({
                    'label': info[2],
                    'background_image': Image.open(f'{path}/{file}'),
                    'author': info[1],
                })

        # Get user profile picture
        user_asset: discord.Asset = interaction.user.display_avatar.with_size(256)
        data = BytesIO(await user_asset.read())
        # Check for profile picture type
        old_pfp = Image.open(data)
        is_gif: bool = isGif(old_pfp)

        background_image = options[0]['background_image']
        new_pfp: list | PngImagePlugin.PngImageFile = process_gif(old_pfp, background_image) if is_gif else \
                                                        process_static_image(old_pfp, background_image)

        # Create embed
        extension: str = 'gif' if is_gif else 'png'
        embed: discord.Embed = discord.Embed(
            title='Pride',
            description=f'{interaction.user.mention}\n*1. Click on image to save.\n2. Right click and save.\n3. Change your profile picture in Discord settings.*',
            color=discord.Color(0xa7c7e7),
        )
        embed.set_image(url=f'attachment://pfp.{extension}')
        embed.set_footer(text=f'Designed by {options[0]["author"]}.')
        view: discord.ui.View = SelectionView(self.bot, options)

        # Send image
        with BytesIO() as image_binary:
            if is_gif:
                new_pfp[0].save(image_binary, format=extension, save_all=True, append_images=new_pfp[1:], duration=100, loop=0)
            else:
                new_pfp.save(image_binary, extension.upper())
            image_binary.seek(0)
            await interaction.response.send_message(
                file=discord.File(fp=image_binary, filename=f'pfp.{extension}'), 
                embed=embed, 
                view=view,
                ephemeral=True
            )


    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PFP(bot))