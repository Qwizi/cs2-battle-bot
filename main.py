from email.policy import default
import json
from multiprocessing import Value
import os
import random
import discord
import httpx
from dotenv import load_dotenv
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

guild_id = 639034263999741953

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[guild_id])
async def losuj(ctx):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
        return
    voice_channel = ctx.author.voice.channel

    # Fetch the members in the voice channel
    members = voice_channel.members

    print(members)
    # Shuffle the list of members
    random.shuffle(members)

    # Split the list of members into two teams
    num_members = len(members)
    middle_index = num_members // 2
    team1 = members[:middle_index]
    team2 = members[middle_index:]

    # Create a list of member names for each team
    team1_names = [member.name for member in team1]
    team2_names = [member.name for member in team2]
    # Send the list of member names as a response
    await ctx.send(f"Team 1: {', '.join(team1_names)} \nTeam 2: {', '.join(team2_names)}")

@bot.slash_command(guild_ids=[guild_id])
async def connect(ctx):
    await ctx.send("[Połącz konto](https://cs2.sharkservers.pl/accounts/discord/)")


@bot.slash_command(guild_ids=[guild_id])
async def create(ctx, team1_name: discord.Option(str, default="Team1"), team2_name: discord.Option(str, default="Team2"), maplist: discord.Option(str, default="de_mirage,de_nuke")):
    await ctx.defer()
    map_list = maplist.split(",")
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
        return
    # Fetch the members in the voice channel
    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    async with httpx.AsyncClient(base_url=os.environ.get("API_URL")) as client:
        # if len(members) <= 1:
        #     await ctx.send("You need at least 2 players to create a match.")
        #     return
        discord_users_ids = [member.id for member in members]
        discord_users_ids.append(ctx.author.id)
        response = await client.post("/matches/", json={"discord_users_ids": [member.id for member in members], "team1_name": team1_name, "team2_name": team2_name, "maplist": maplist})
        data = response.json()
        print(response)
        if response.status_code == 201:
            team1 = data.get("team1")
            team2 = data.get("team2")

            if not team1 or not team2:
                await ctx.send("Brakuje graczy do utworzenia meczu.")
                return
            print(team1)
            print(team2)
            team1_names = []

            for player in team1["players"]:
                player_name = None
                for key, value in player.items():
                    player_name = value

                team1_names.append(player_name)

            team2_names = []
            for player in team2["players"]:
                player_name = None
                for key, value in player.items():
                    player_name = value
                team2_names.append(player_name)
            
            embed = discord.Embed(
                title="Mecz utworzony!",
                description="Mecz został utworzony.",
                color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
            )
            embed.add_field(name=team1.get("name", "Team 1"), value=f"{', '.join(team1_names)}", inline=False)
            embed.add_field(name=team2.get("name", "Team 2"), value=f"{', '.join(team2_names)}", inline=False)
            embed.add_field(name="Mapy", value=f"{', '.join(map_list)}", inline=False)
            await ctx.followup.send("Match created", embed=embed)
        else:
            await ctx.followup.send("Error creating match")

bot.run(os.environ.get('TOKEN'))