import discord
from django.core.management import BaseCommand

from bot.utils import guild_exists, create_guild
from cs2_battle_bot import settings

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    for guild in client.guilds:
        if not await guild_exists(guild.id):
            await create_guild(guild.name, guild.id)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


class Command(BaseCommand):
    help = "Run the bot"

    def handle(self, *args, **options):
        client.run(settings.BOT_TOKEN)
