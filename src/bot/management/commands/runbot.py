import asyncio

import discord
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from loguru import logger

from cs2_battle_bot import settings
from guilds.models import Guild

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)

User = get_user_model()

async def sync_guild(guild):
    guild_db, created = await Guild.objects.aget_or_create(name=guild.name, gid=str(guild.id))
    await guild_db.sync_members(guild)
    await guild_db.sync_owner(guild)

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    logger.info(f"Bot added to {len(client.guilds)} guilds")
    
    for dc_guild in client.guilds:
        logger.info(f"Syncing guild {dc_guild.name}")
        await sync_guild(dc_guild)
        logger.info(f"Guild {dc_guild.name} synced")


@client.event
async def on_guild_join(guild: discord.Guild):
    logger.info(f"Bot joined guild {guild.name}")
    logger.info(f"Syncing guild {guild.name}")
    await sync_guild(guild)
    logger.info(f"Guild {guild.name} synced")


class Command(BaseCommand):
    help = "Run the bot"

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.run(settings.BOT_TOKEN))
