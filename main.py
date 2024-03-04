import os
import discord
from dotenv import load_dotenv
import redis
from cogs.match import MatchCog

load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


_redis = redis.StrictRedis(host="redis", port=6379, db=0)

pubsub = _redis.pubsub()
pubsub.psubscribe("event.*")
bot.add_cog(MatchCog(bot, pubsub))
bot.run(os.environ.get("TOKEN"))
