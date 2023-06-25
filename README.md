# BetterPFP
BetterPFP creates themed profile pictures for your Discord account. This works for both static and animated profile pictures.

Currently there is one theme available which is `/pride` for Pride Month. Stay tuned for more themes or add your own.

[Add BetterPFP to your Discord server](https://discord.com/api/oauth2/authorize?client_id=1116051237029294191&permissions=51264&scope=bot%20applications.commands)

## Built Using
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- PostgreSQL
- PIL

## Local Deployment
If you would like to host your own instance of the bot, please do the following:

First create a discord application [here](https://discord.com/developers/applications).

Create a `.env` file in `src/` directory with the following:
```
APPLICATION_ID="XXX"     # your discord application client ID
BOT_TOKEN="XXX"          # your discord application token 
OWNER_ID="XXX"           # your discord account ID
SUPPORT_GUILD_ID="XXX"   # bot support server ID
VERSION=1.0.0            # version
```

Then install the latest version of Python [here](https://www.python.org/downloads/).

Next, clone this repo and navigate to the root and create the a virtual environment by running one of the following:
```
py -m venv venv
python -m venv venv # Try this if the above does NOT work
python3 -m venv venv  # Try this if the above two do NOT work
```

Once created, run the following command in your terminal:
```
venv\scripts\activate.bat
```

Then run:
```
pip install requirements.txt
```

And finally start the bot:
```
py src\bot.py
python src\bot.py # If the above does NOT work
python3 src\bot.py # If the above two do NOT work
```

## Configuring the bot
Once you have the bot up and running, simply run `bp!sync` to sync all slash commands globally.

And you're done!

### Adding more themes
To add more themes, create a new folder within `src/resources`, copy and paste the `Pride` command and edit the following:
```python
@app_commands.command(name=[INSERT COMMAND NAME], description=[INSERT DESCRIPTION])
...
async def [INSERT NEW FUNCTION NAME](self, interaction: discord.Interaction) -> None:
...
path: str = './src/resources/[NAME OF FOLDER YOU MADE]'
...
embed: discord.Embed = discord.Embed(
    title=[INSERT THEME NAME],
    description=f'{interaction.user.mention}\n*Click on image to save.*',
    color=discord.Color(0xa7c7e7),
)
```
Rerun the bot and sync all commands again.

And you're done!

## Next Steps
I want to add an easier way to add new themes.
