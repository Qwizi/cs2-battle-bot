import os
import random
import discord
from dotenv import load_dotenv
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[639034263999741953])
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


bot.run(os.environ.get('TOKEN'))