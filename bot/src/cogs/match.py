"""Match Cog."""

from __future__ import annotations

import json
from http import HTTPStatus

import discord
from cs2_battle_bot_api_client.api.account_connect_link import (
    account_connect_link_retrieve,
)
from cs2_battle_bot_api_client.api.guilds import guilds_retrieve
from cs2_battle_bot_api_client.api.matches import matches_create, matches_update
from cs2_battle_bot_api_client.errors import UnexpectedStatus
from cs2_battle_bot_api_client.models import (
    AccountConnectLink,
    CreateMatch,
    CreateMatchCvars,
    Match,
    MatchTypeEnum,
)
from cs2_battle_bot_api_client.models.match_update import MatchUpdate
from cs2_battle_bot_api_client.types import Response
from discord.commands import option
from discord.ext import commands, tasks
from events.events import (
    OnGoingLiveEvent,
    OnMapResultEvent,
    OnSeriesEndEvent,
    OnSeriesStartEvent,
)
from events.listener import EventListener
from i18n import _
from logger import logger
from redis.client import PubSub
from settings import api_client, settings

from cogs.utils import create_match_embed, get_servers_list
from cogs.views import ConfigureGuildView, LaunchMatchView, MapBanView


class MatchCog(commands.Cog):
    """Match Cog."""

    def __init__(self, bot: discord.Bot, pubsub: PubSub) -> None:
        """Match Cog constructor."""
        self.bot = bot
        self.pubsub = pubsub
        self.listen_events.start()

    match = discord.SlashCommandGroup(
        name="match", description="Commands for managing matches"
    )

    @match.command()
    async def link(self, ctx: discord.ApplicationContext) -> None:
        """
        Get connect account link command.

        Args:
        ----
                ctx (discord.ApplicationContext): Application context.

        Returns:
        -------
                None

        """
        connect_account_link: AccountConnectLink = (
            await account_connect_link_retrieve.asyncio(
                client=api_client,
            )
        )
        link = (
            connect_account_link.link
            if not settings.DEBUG
            else "http://localhost:8002/accounts/discord/"
        )
        await ctx.respond(
            f"[{_('connect_account')}]({link})",
            ephemeral=True,
        )

    @match.command()
    async def configure(self, ctx: discord.ApplicationContext) -> None:
        """Configure guild command. Select channels for lobby, team1 and team2."""
        await ctx.defer()
        guild = await guilds_retrieve.asyncio(
            client=api_client, guild_id=str(ctx.guild.id)
        )

        if ctx.author.id != int(guild.owner.player.discord_user.user_id):
            await ctx.followup.send(_("error_user_is_not_owner"), ephemeral=True)
            return

        guild_embed = discord.Embed(
            title=f"Guild configuration for {ctx.guild.name}",
            description="Select channels for lobby, team1 i team2",
            color=discord.Color.green(),
        )

        for name, channel in [
            ("Lobby", guild.lobby_channel),
            ("Team 1", guild.team1_channel),
            ("Team 2", guild.team2_channel),
        ]:
            guild_embed.add_field(
                name=name,
                value=ctx.guild.get_channel(int(channel)).mention
                if channel
                else "Brak",
                inline=False,
            )

        await ctx.followup.send(embed=guild_embed, view=ConfigureGuildView(guild=guild))

    @match.command()
    @option(
        "match_type",
        type=str,
        choices=[
            discord.OptionChoice(name="BO1", value="BO1"),
            discord.OptionChoice(name="BO3", value="BO3"),
        ],
        default="BO1",
    )
    @option(
        "maplist", type=str, required=False, description="Maplist separated by comma"
    )
    @option(
        "sides",
        type=str,
        required=False,
        description="Sides separated by comma. Valid values: team1_ct, team1_t, team2_ct, team2_t, knife",
    )
    @option(
        "cvars",
        type=str,
        required=False,
        description="Cvars separated by comma. Example: mp_maxrounds=30,mp_startmoney=800",
    )
    @option(
        "server",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(get_servers_list),
        required=False,
        description="Public available server",
    )
    async def create(
        self,
        ctx: discord.ApplicationContext,
        match_type: str,
        maplist: str,
        sides: str,
        cvars: str,
        server: str,
    ) -> None:
        """
        Create match command.

        Args:
        ----
            ctx (discord.ApplicationContext): Application context.
            match_type (str): Match type.
            maplist (str): Maplist.
            sides (str): Sides.
            cvars (str): Cvars.
            server (str): Server.

        """
        await ctx.defer()
        if not ctx.author.voice:
            await ctx.followup.send(
                _("error_user_is_not_in_voice_channel"), ephemeral=True
            )
            return

        members = ctx.author.voice.channel.members
        if not settings.DEBUG and len(members) < settings.MIN_PLAYERS:
            await ctx.followup.send(
                _("error_min_members_count", settings.MIN_PLAYERS), ephemeral=True
            )
            return

        discord_users_ids = (
            [member.id for member in members]
            if not settings.DEBUG
            else [ctx.author.id, 859429903170273321, 692055783650754650]
        )
        guild = await guilds_retrieve.asyncio(
            client=api_client, guild_id=str(ctx.guild.id)
        )
        server_id = server.split(":")[1] if server else None

        create_match_data = CreateMatch(
            match_type=MatchTypeEnum(match_type),
            discord_users_ids=discord_users_ids,
            author_id=ctx.author.id,
            guild_id=guild.id,
        )

        if server:
            create_match_data.server_id = server_id

        if maplist:
            maplist_split = maplist.split(",")
            if match_type == "BO1" and len(maplist_split) != 1:
                await ctx.followup.send(_("error_maplist_bo1"), ephemeral=True)
                return
            if match_type == "BO3" and len(maplist_split) != 3:
                await ctx.followup.send(_("error_maplist_bo3"), ephemeral=True)
                return
            create_match_data.maplist = maplist_split

        if sides:
            sides_split = sides.split(",")
            create_match_data.map_sides = sides_split

        if cvars:
            cvars_dict = {}
            if "," not in cvars:
                cvar_detail = cvars.split("=")
                if len(cvar_detail) != 2:
                    return
                cvars_dict[cvar_detail[0]] = cvar_detail[1]
            else:
                cvars_split = cvars.split(",")
                if len(cvars_split) == 0:
                    return
                for cvar in cvars_split:
                    cvar_detail = cvar.split("=")
                    if len(cvar_detail) != 2:
                        return
                    cvars_dict[cvar_detail[0]] = cvar_detail[1]
                if len(cvars_dict) == 0:
                    return
            create_match_data.cvars = CreateMatchCvars.from_dict(cvars_dict)

        try:
            response: Response[Match] = await matches_create.asyncio_detailed(
                client=api_client, body=create_match_data
            )
            if response.status_code != HTTPStatus.CREATED:
                await ctx.followup.send(
                    response.content.decode(encoding="utf-8"), ephemeral=True
                )
                return
        except UnexpectedStatus as e:
            data = (
                json.loads(e.content.decode(encoding="utf-8"))
                if isinstance(e.content, bytes)
                else e.content
            )
            if isinstance(data, dict) and (users := data.get("users")):
                await ctx.followup.send(
                    _(
                        "error_users_not_exists",
                        ", ".join([f"<@{user}>" for user in users]),
                    ),
                    ephemeral=True,
                )
            else:
                await ctx.followup.send(data, ephemeral=True)
            logger.error(repr(e))
            return

        match = response.parsed
        match_embed = create_match_embed(match)
        message = await ctx.followup.send(
            embed=match_embed,
            view=MapBanView(
                options=[
                    discord.SelectOption(label=map.tag, value=map.tag)
                    for map in match.maps
                ],
                match=match,
            )
            if not maplist
            else LaunchMatchView(timeout=None, match=match),
            allowed_mentions=discord.AllowedMentions(users=True, roles=True),
        )

        logger.debug(
            f"User {ctx.author.id} created match  of type {match_type} with members {discord_users_ids}. Message id {message.id}"
        )
        await matches_update.asyncio(
            client=api_client, id=match.id, body=MatchUpdate(message_id=message.id)
        )
        logger.debug(f"Match updated: {message.id}")

    @tasks.loop(seconds=5)
    async def listen_events(self) -> None:
        """
        Listen events. Every 5 seconds.

        Available events:
        - going_live
        - series_start
        - series_end
        - map_result
        - round_end
        - side_picked
        - map_picked
        - map_vetoed

        Args:
        ----
            None

        Returns:
        -------
            None

        """
        event_listener = EventListener(
            [
                OnGoingLiveEvent(self.bot, "going_live"),
                OnSeriesStartEvent(self.bot, "series_start"),
                OnSeriesEndEvent(self.bot, "series_end"),
                OnMapResultEvent(self.bot, "map_result"),
            ],
            pubsub=self.pubsub,
        )
        try:
            await event_listener.listen()
        except Exception as e:
            logger.error(repr(e))

    @listen_events.before_loop
    async def before_listen_events(self) -> None:
        """Before listen events."""
        await self.bot.wait_until_ready()
        print("Starting listening events")

    @listen_events.after_loop
    async def after_listen_events(self) -> None:
        """After listen events."""
        print("Stopped listening events")
