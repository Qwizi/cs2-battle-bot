"""CS2 Battle Bot main module."""

import discord
import redis
import sentry_sdk
from redis import ConnectionError, TimeoutError

from bot.bot import bot
from bot.cogs.match import MatchCog
from bot.i18n import i18n
from bot.logger import logger
from bot.settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment="production" if not settings.TESTING else "development",
)


@bot.event
async def on_ready() -> None:
    """Print a message when the bot is ready."""
    logger.debug(f"We have logged in as {bot.user}")


@bot.event
async def on_application_command_error(
    ctx: discord.ApplicationContext, error: discord.DiscordException
) -> None:
    """
    Handle errors that occur while processing a command.

    Args:
    ----
        ctx (discord.ApplicationContext): The context in which the command was invoked.
        error (discord.DiscordException): The error that occurred.

    Returns:
    -------
        None: This function does not return anything.

    """
    logger.error(repr(error))
    sentry_sdk.capture_exception(error)
    await ctx.respond("An error occurred while processing the command.")


try:
    _redis = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    )
    response = _redis.ping()
    pubsub = _redis.pubsub()
    pubsub.psubscribe("event.*")
    bot.add_cog(MatchCog(bot, pubsub))
    logger.debug(f"Connected to Redis: {response}")
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Redis connection error: {e}")
    # Handle the error appropriately, e.g., retrying or logging
    sentry_sdk.capture_exception(e)
i18n.localize_commands()
bot.run(settings.TOKEN)
