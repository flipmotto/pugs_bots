import discord
import io
from discord.ext import commands
import json

TOKEN = None

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)

GUILD = None

emojis = ['😀','👍', '👎']
embed = discord.Embed(title="Example Embed", description="This is an example embed message.")


# username: {"elo": 1000, "weight": 1}
ELO_MAP = {
}

@bot.event
async def on_ready():
    global GUILD
    print(f"logged in as {bot.user}")

    GUILD = bot.get_guild(1118732200603557958)

    load_map()

    print(ELO_MAP)


def get_players_from_vc(channel_name):
    target_channel = discord.utils.get(GUILD.channels, name=channel_name)

    voice_states = target_channel.voice_states

    return [bot.get_user(x).name for x in voice_states.keys()]



def add_user(username):
    ELO_MAP[username] = {
        "elo": 1000,
        "weight": 1
    }

    return ELO_MAP[username]
    
def user_exists(username):
    return username in ELO_MAP.keys()

def get_user(username):
    if not user_exists(username):
        return add_user(username)
    else:
        return ELO_MAP[username]
    
#racism2.0

def save_map():
    with open('elo.json', 'w') as file:
        json.dump(ELO_MAP, file, indent=4)

def load_map():
    global ELO_MAP
    with open('elo.json', 'r') as file:
        ELO_MAP = json.load(file)

@bot.command()
async def get_players(ctx):
    add_user(ctx.author.name)
    save_map()

@bot.command()
async def change_channel(ctx):
    pass

@bot.event
async def win_reaction(reaction, users):
    embed = reaction.embeds[0]
    emoji = reaction.emoji

    if users.bot:
        return


if __name__ == '__main__':
    bot.run(TOKEN)