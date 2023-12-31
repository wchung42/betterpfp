import discord
from discord.ext import commands
import asyncio
import aiohttp
import os
import logging
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PREFIX = 'bp!'

# Enable Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#--------------------------------------------------------------------
# Main Bot Class
#--------------------------------------------------------------------
class BetterPFP(commands.Bot):
    def __init__(self, session):
        super().__init__(
            command_prefix=DEFAULT_PREFIX,
            intents=intents,
            application_id=int(os.getenv('APPLICATION_ID')),
            owner_id=int(os.getenv('OWNER_ID')),
            activity=discord.Activity(type=discord.ActivityType.playing, name='with pfps.'), 
            status=discord.Status.online,
            help_command=None,
        )
        self.session = session
        self.config_token = str(os.getenv('BOT_TOKEN'))
        self.version = str(os.getenv('VERSION'))
        self.DEFAULTPREFIX = DEFAULT_PREFIX
        self.support_guild_id = os.getenv('SUPPORT_GUILD_ID')

        logging.basicConfig(level=logging.INFO)

        self.initial_extensions = []
        for file in os.listdir('./src/cogs'):
            if file.endswith('.py'):
                self.initial_extensions.append(f'cogs.{file[:-3]}')
    

    async def get_prefix(self, message):
        if not message.guild:
            return commands.when_mentioned_or(DEFAULT_PREFIX)(self, message)

        # Fetch prefix from DB
        prefix: str = DEFAULT_PREFIX
        # async with self.db.acquire() as conn:
        #     tr = conn.transaction()
        #     await tr.start()
        #     try:
        #         query: str = 'SELECT prefix FROM guilds WHERE guild_id = $1'
        #         prefix: str = await self.db.fetchval(query, message.guild.id)
        #         if not prefix:
        #             query = 'INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)'
        #             await self.db.execute(query, message.guild.id, DEFAULT_PREFIX)
        #     except asyncpg.PostgresError as e:
        #         await tr.rollback()
        #         await postgres.send_postgres_error_embed(self, query, e)
        #     else:
        #         await tr.commit()
        return commands.when_mentioned_or(prefix)(self, message)


    # Setup function
    async def setup_hook(self) -> None:
        print('Running setup...')
        self.session = aiohttp.ClientSession()
        
        # Load all cogs
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        print('Setup complete.')


    async def close(self) -> None:
        await super().close()
        await self.session.close()


    async def on_ready(self) -> None:
        await self.wait_until_ready()
        print('Online.')


    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id: # ignore self
            return
        # if isinstance(message.channel, discord.DMChannel): # ignore dms
        #     return
        await self.process_commands(message)


#--------------------------------------------------------------------
# Main driver function
#--------------------------------------------------------------------
async def main():
    async with aiohttp.ClientSession() as session:
        async with BetterPFP(session) as bot:
            await bot.start(bot.config_token, reconnect=True)


asyncio.run(main())