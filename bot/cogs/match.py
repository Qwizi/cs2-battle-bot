"""Match Cog."""

from __future__ import annotations

import discord
import httpx
from discord.ext import commands, tasks
from pydantic import ValidationError
from redis.client import PubSub  # noqa: TCH002

from bot.api import (
    create_match,
    get_connect_account_link,
    get_curent_match,
)
from bot.cogs.views import MapBanView
from bot.events.going_live import OnGoingLiveEvent
from bot.events.listener import EventListener
from bot.schemas import CreateMatch
from bot.settings import settings

TESTING = settings.TESTING


guild_id = 639034263999741953
info_channel_id = 1210935599972749312
status_message_id = 1213212463563280454
general_channel_id = 1211078909127561257
lobby_channel_id = 1211059521762492486
team1_channel_id = 1211059841993281537
team2_channel_id = 1211059895202484344


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

    @match.command(guild_ids=[guild_id])
    async def connect(self, ctx: discord.ApplicationContext) -> None:
        """
        Get connect account link command.

        Args:
        ----
            ctx (discord.ApplicationContext): Application context.

        Returns:
        -------
            None

        """
        connect_account_link = get_connect_account_link()
        await ctx.respond(f"[Połącz konto]({connect_account_link})", ephemeral=True)

    @match.command(guild_ids=[guild_id])
    async def create(
        self,
        ctx: discord.ApplicationContext,
        match_type: str = discord.Option(
            str,
            choices=[
                discord.OptionChoice(name="BO1", value="BO1"),
                discord.OptionChoice(name="BO3", value="BO3"),
                discord.OptionChoice(name="BO5", value="BO5"),
            ],
            default="BO1",
            name="match_type",
        ),
    ) -> None:
        """
        Create match command.

        Args:
        ----
            ctx (discord.ApplicationContext): Application context.
            match_type (discord.Option): Match type.


        Returns:
        -------
            None

        """
        await ctx.defer()
        if ctx.author.voice is None:
            await ctx.followup.send("Nie jestes na kanale glosowym.", ephemeral=True)
            return
        voice_channel = ctx.author.voice.channel
        members = voice_channel.members
        if TESTING is False and len(members) < settings.MIN_PLAYERS:
            await ctx.followup.send(
                "Wymange 2 graczy, by rozpoczac mecz", ephemeral=True
            )
            return
        await self._create_match(ctx, match_type, members)

    async def _create_match(
        self,
        ctx: discord.ApplicationContext,
        match_type: str,
        members: list[discord.Member],
    ) -> None:
        """
        Create match.

        Args:
        ----
            ctx (discord.ApplicationContext): Application context.
            match_type (str): Match type.
            members (list[discord.Member]): List of members.

        Returns:
        -------
            None

        """
        try:
            discord_users_ids = [member.id for member in members]
            if TESTING:
                discord_users_ids = [
                    ctx.author.id,
                    859429903170273321,
                    692055783650754650,
                ]

            api_token = settings.API_TOKEN
            webhook_url = f"{settings.API_URL}/api/matches/webhook/"

            # Create match
            try:
                created_match, _ = await create_match(
                    data=CreateMatch(
                        discord_users_ids=discord_users_ids,
                        shuffle_teams=True,
                        match_type=match_type,
                        map_sides=["knife", "knife", "knife"],
                        cvars={
                            "matchzy_remote_log_url": webhook_url,
                            "matchzy_remote_log_header_key": "X-Api-Key",
                            "matchzy_remote_log_header_value": api_token,
                        },
                    )
                )

                # Send match embed and map ban view
                match_embed = created_match.create_match_embed(ctx.author.id)
                map_ban_view = MapBanView(
                    options=[
                        discord.SelectOption(label=tag, value=tag)
                        for tag in created_match.get_maps_tags()
                    ],
                    match=created_match,
                )

                await ctx.followup.send(embed=match_embed, view=map_ban_view)

            except httpx.HTTPError as exc:
                self.handle_http_error(exc, ctx)
            except ValidationError as exc:
                await ctx.followup.send(
                    "ValidationError: Failed to create match", ephemeral=True
                )
                print(repr(exc))
        except (discord.errors.HTTPException, AttributeError) as exc:
            print(repr(exc))
            await ctx.followup.send(
                f"{type(exc).__name__}: Failed to create match", ephemeral=True
            )

    async def handle_http_error(
        self, exc: httpx.HTTPError, ctx: discord.ApplicationContext
    ) -> None:
        """Handles HTTP errors gracefully."""
        data = exc.response.json()
        message = data.get("message")

        if message and "Discord user" in message:
            user_id = data.get("user_id")
            await ctx.followup.send(
                f"Uzytkownik <@{user_id}> nie jest zarejestrowany w bazie danych"
            )
        else:
            await ctx.followup.send(
                f"HTTP {exc.response.status_code}: Failed to create match",
                ephemeral=True,
            )
        print(data)

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
            [OnGoingLiveEvent(self.bot, "going_live")], pubsub=self.pubsub
        )
        await event_listener.listen()

    @listen_events.before_loop
    async def before_listen_events(self) -> None:
        """Before listen events."""
        await self.bot.wait_until_ready()
        print("Starting listening events")

    @listen_events.after_loop
    async def after_listen_events(self) -> None:
        """After listen events."""
        print("Stopped listening events")
