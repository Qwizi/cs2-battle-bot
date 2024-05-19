"""Utility functions for the src."""

from __future__ import annotations

import discord
from cs2_battle_bot_api_client.api.guilds import guilds_retrieve
from cs2_battle_bot_api_client.api.servers import servers_list
from cs2_battle_bot_api_client.models import Match
from cs2_battle_bot_api_client.models.guild import Guild
from cs2_battle_bot_api_client.models.paginated_server_list import PaginatedServerList
from cs2_battle_bot_api_client.types import Response
from i18n import _
from settings import api_client, settings


def get_connect_account_link() -> str:
    """
    Get connect account link.

    Returns
    -------
        str: Connect account link.

    """
    return (
        "http://localhost:8002/accounts/discord/"
        if settings.DEBUG
        else f"{settings.API_URL}/accounts/discord/"
    )


def create_match_embed(match: Match) -> discord.Embed:
    """
    Create match embed.

    Args:
    ----
        match (Match): Match object.

    Returns:
    -------
        discord.Embed: Embed with match information.

    """
    embed = discord.Embed(
        title=_("embed_match_title"),
        description=_("embed_match_desc", match.id, match.type),
        color=discord.Colour.blurple(),
    )

    teams = [match.team1, match.team2]
    for team in teams:
        mentioned_leader = f"<@{team.leader.discord_user.user_id}>"
        mentioned_players = [
            f"<@{player.discord_user.user_id}>" for player in team.players
        ]
        embed.add_field(
            name=team.name,
            value=", ".join(mentioned_players),
            inline=False,
        )
        embed.add_field(
            name=_("leader"),
            value=mentioned_leader,
            inline=False,
        )
    embed.add_field(
        name=_("maps"),
        value=", ".join(match.maplist),
        inline=False,
    )
    return embed


async def get_servers_list(ctx: discord.AutocompleteContext) -> list[str]:
    """
    Get servers list.

    Args:
    ----
        ctx (discord.AutocompleteContext): Autocomplete context.

    Returns:
    -------
        list[str]: List of servers.

    """
    guild: Guild = await guilds_retrieve.asyncio(
        client=api_client, guild_id=str(ctx.interaction.guild_id)
    )
    response: Response[PaginatedServerList] = await servers_list.asyncio_detailed(
        client=api_client, guild_or_public=guild.id
    )

    paginated_servers = response.parsed
    return [f"{server.name}:{server.id}" for server in paginated_servers.results]
