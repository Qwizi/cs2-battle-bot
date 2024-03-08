"""CS2 Battle Bot main module."""

import discord
import redis
from dotenv import load_dotenv

from bot.cogs.match import MatchCog
from bot.settings import settings

load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    """Print a message when the bot is ready."""
    print(f"We have logged in as {bot.user}")


_redis = redis.StrictRedis(host="redis", port=6379, db=0)

pubsub = _redis.pubsub()
pubsub.psubscribe("event.*")
bot.add_cog(MatchCog(bot, pubsub))
bot.run(settings.TOKEN)
