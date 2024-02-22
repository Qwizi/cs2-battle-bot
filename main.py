import json
import os
import random
from urllib import response
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
async def create(ctx):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
        return
    # Fetch the members in the voice channel
    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    async with httpx.AsyncClient(base_url=os.environ.get("API_URL")) as client:
        response = await client.post("/matches/", json={"discord_users_ids": [member.id for member in members]})
        data = response.json()
        if response.status_code == 200:
            data = json.loads(data)
            team1 = data.get("team1")
            team2 = data.get("team2")

            if not team1 or not team2:
                await ctx.send("Error creating match")
                return
            
            team1_names = []

            for player in team1:
                player  = json.loads(player)
                discord_user = player.get("discord_user")
                mentioned_username = f"<@{discord_user.get('user_id')}>"

                team1_names.append(mentioned_username)

            team2_names = []
            for player in team2:
                player  = json.loads(player)
                discord_user = player.get("discord_user")
                mentioned_username = f"<@{discord_user.get('user_id')}>"
                team2_names.append(mentioned_username)
            
            embed = discord.Embed(
                title="Mecz utworzony!",
                description="Mecz został utworzony.",
                color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
            )
            embed.add_field(name="Drużyny", value="Zostały rozlosowane drużyny")
            embed.add_field(name="Team 1", value=f"{', '.join(team1_names)}", inline=True)
            embed.add_field(name="Team 2", value=f"{', '.join(team2_names)}", inline=True)
            await ctx.send("Match created", embed=embed)
            await ctx.send("Match created")
        else:
            await ctx.send("Error creating match")

bot.run(os.environ.get('TOKEN'))