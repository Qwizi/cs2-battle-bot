import discord
from django.contrib.auth import get_user_model

from guilds.services import create_guild_if_not_exists

client = discord.Bot(intents=discord.Intents.all())

User = get_user_model()


@client.event
async def on_ready():
    for guild in client.guilds:
        await create_guild_if_not_exists(guild.owner.name, guild.id, guild.name)
    print(f"We have logged in as {client.user}")


@client.event
async def on_guild_join(guild):
    await create_guild_if_not_exists(guild.owner.name, guild.id, guild.name)
