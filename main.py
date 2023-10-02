import discord
import io
from discord.ext import commands
import json
import itertools

TOKEN = None

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)

GUILD = None

emojis = ['😀','👍', '👎']
embed = discord.Embed(title="Example Embed", description="This is an example embed message.")


# {username: {"elo": 1000, "weight": 1} etc}
ELO_MAP = {
}

@bot.event
async def on_ready():
    global GUILD
    print(f"logged in as {bot.user}")

    GUILD = bot.get_guild(1118732200603557958)

    #load_map()
    #save_map()
    load_test()
    save_test()


    matches = optimize_matches(generate_all_matches())

    for match in matches:
        display_match(match)


# TODO everything here is really fucking shit and unorganized
# TODO match log, improve optimization algorithm
# TODO determine win and loss elo
# TODO determine how to update weight
# TODO improve display_match
# TODO lots of stuff fuck
# TODO send out message with the top optimal teams
# TODO react for which one to pick
# TODO once a match is set automatically move people to correct vc
# TODO send out another message asking which team won

def get_players_from_vc(channel_name):
    target_channel = discord.utils.get(GUILD.channels, name=channel_name)

    voice_states = target_channel.voice_states

    return [bot.get_user(x).name for x in voice_states.keys()]

def optimize_matches(matches):
     def match_sort_key(match):
        team1_elo = sum(player_info["elo"] for player_info in match["team1"].values())
        team2_elo = sum(player_info["elo"] for player_info in match["team2"].values())
        
        # Calculate the total weight for each team
        team1_weight = sum(player_info["weight"] for player_info in match["team1"].values())
        team2_weight = sum(player_info["weight"] for player_info in match["team2"].values())
        
        # Calculate the difference in ELOs between the teams
        elo_difference = abs(team1_elo - team2_elo)
        
        # Calculate the difference in weights between the teams
        weight_difference = abs(team1_weight - team2_weight)
        
        # Combine ELO and weight differences for sorting
        return elo_difference + weight_difference
     
     return sorted(matches, key=match_sort_key)

def generate_all_matches():
    combinations = list(itertools.combinations(ELO_MAP.keys(), 4))
    matches = []
    generated_teams = set()

    for combination in combinations:
        team1_combinations = list(itertools.combinations(combination, 2))
        for team1 in team1_combinations:
            team2 = tuple(player for player in combination if player not in team1)
            
            # Ensure that team2 is not a duplicate of team1
            if team2 not in generated_teams:
                match = {
                    "team1": {player: ELO_MAP[player] for player in team1},
                    "team2": {player: ELO_MAP[player] for player in team2},
                }
                matches.append(match)
                generated_teams.add(team1)
                generated_teams.add(team2)
    return matches

def display_match(match):
    print(f"Team 1: {get_team_elo(match['team1']):.0f} elo")
    for player, info in match["team1"].items():
        print(f"Player: {player}, ELO: {info['elo']}")
    

    print(f"Team 2: {get_team_elo(match['team2']):.0f} elo")
    for player, info in match["team2"].items():
        print(f"Player: {player}, ELO: {info['elo']}")

    print("\n")

def get_team_elo(team):
    total = 0
    for player in team.values():
        total+= player['elo']
    
    return total/len(team.keys())

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

def save_test():
    with open('test.json', 'w') as file:
        json.dump(ELO_MAP, file, indent=4)

def load_test():
    global ELO_MAP
    with open('test.json', 'r') as file:
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