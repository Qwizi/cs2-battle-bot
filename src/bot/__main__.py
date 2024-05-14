"""CS2 Battle Bot main module."""

import discord
import redis
from cogs.match import MatchCog
from cs2_battle_bot_api_client.api.guilds import guilds_create, guilds_retrieve
from cs2_battle_bot_api_client.errors import UnexpectedStatus
from cs2_battle_bot_api_client.models import CreateGuild, Guild
from cs2_battle_bot_api_client.types import Response
from i18n import i18n
from logger import logger
from redis import ConnectionError, TimeoutError
from settings import api_client, settings

from bot import bot


@bot.event
async def on_ready() -> None:
    """Print a message when the bot is ready."""
    logger.debug(f"We have logged in as {bot.user}")


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    """
    Handle the bot joining a guild.

    Args:
    ----
        guild (discord.Guild): The guild the bot joined.

    Returns:
    -------
        None: This function does not return anything.

    """
    logger.info(f"Bot joined guild: {guild.name}")
    try:
        await guilds_retrieve.asyncio_detailed(
            client=api_client, guild_id=str(guild.id)
        )
    except UnexpectedStatus:
        new_guild_response: Response[Guild] = await guilds_create.asyncio_detailed(
            client=api_client,
            body=CreateGuild(
                guild_id=str(guild.id),
                name=guild.name,
                owner_id=str(guild.owner_id),
                owner_username=guild.owner.name,
            ),
        )
        logger.info(
            f"Guild {new_guild_response.content.decode(encoding='utf-8') } created."
        )


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
    logger.error(error)
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
i18n.localize_commands()
bot.run(settings.DISCORD_BOT_TOKEN)
