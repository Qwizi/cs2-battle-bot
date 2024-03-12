"""Event listener for the bot."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

import discord
from prettytable import PrettyTable
from redis.client import PubSub  # noqa: TCH002

from bot import logger
from bot.schemas import Match, Player
from bot.settings import settings


class Event(ABC):
    """Base class for events."""

    def __init__(self, bot: discord.Bot, name: str) -> None:
        """
        Event constructor.

        Args:
        ----
            bot (discord.Bot): Bot instance.
            name (str): Event name.
            matchid (int): Match ID.

        Returns:
        -------
            None

        """
        self.bot = bot
        self.name = name
        self.lobby_channel = self.bot.get_channel(settings.LOBBY_CHANNEL_ID)
        self.team1_channel = self.bot.get_channel(settings.TEAM1_CHANNEL_ID)
        self.team2_channel = self.bot.get_channel(settings.TEAM2_CHANNEL_ID)

    def raise_match_id_error(self, matchid: str) -> None:
        """
        Raise match id error.

        Args:
        ----
            matchid (str): Match ID.

        Returns:
        -------
            None

        """
        msg = f"Match ID is missing: {matchid}"
        raise ValueError(msg)

    async def move_players_to_lobby_channel(self, match: Match) -> None:
        """
        Move players to the lobby voice channel.

        Args:
        ----
            match (Match): Match object.

        Returns:
        -------
            None

        """
        players = match.team1.players + match.team2.players
        try:
            for player in players:
                member = self.lobby_channel.guild.get_member(
                    player.discord_user.user_id
                )
                await member.move_to(self.lobby_channel)
                logger.logger.debug(f"Moved {member} to lobby")
        except discord.errors.HTTPException as exc:
            logger.logger.error(f"Error moving players to lobby: {exc!r}")

    async def move_player_to_team_channel(
        self, player: Player, team_channel: discord.VoiceChannel
    ) -> None:
        """
        Move player to the team voice channel.

        Args:
        ----
            player (Player): Player object.
            team_channel (discord.VoiceChannel): Team voice channel.

        Returns:
        -------
            None

        """
        member = self.lobby_channel.guild.get_member(player.discord_user.user_id)
        await member.move_to(team_channel)

    async def move_players_to_teams_channel(self, match: Match) -> None:
        """
        Move players to their respective team voice channels.

        Args:
        ----
            match (Match): Match object.

        Returns:
        -------
            None

        """
        for player in match.team1.players:
            try:
                await self.move_player_to_team_channel(player, self.team1_channel)
                logger.logger.debug(f"Moved {player} to team 1 channel")
            except discord.errors.HTTPException as exc:  # noqa: PERF203
                logger.logger.error(f"Error moving players to teams: {exc!r}")
                continue

        for player in match.team2.players:
            try:
                await self.move_player_to_team_channel(player, self.team2_channel)
                logger.logger.debug(f"Moved {player} to team 2 channel")
            except discord.errors.HTTPException as exc:  # noqa: PERF203
                logger.logger.error(f"Error moving players to teams: {exc!r}")
                continue

    def create_players_table(self, players: list[dict]) -> PrettyTable:
        """
        Create a table with players stats.

        Args:
        ----
            players (list[dict]): List of players.

        Returns:
        -------
            PrettyTable: PrettyTable object.

        """
        table = PrettyTable()
        table.field_names = ["Player", "Kills", "Deaths", "Assists", "Score"]
        for player in players:
            player_name = player.get("name")
            table.add_row(
                [
                    f"{player_name:.15}",
                    player.get("stats").get("kills"),
                    player.get("stats").get("deaths"),
                    player.get("stats").get("assists"),
                    player.get("stats").get("score"),
                ]
            )
        return table

    async def create_team_stats_embed(
        self,
        team: dict,
        players_table: PrettyTable,
        winner: bool = False,  # noqa: FBT001, FBT002
    ) -> discord.Embed:
        """
        Create team embed.

        Args:
        ----
            team (dict): Team data.
            players_table (PrettyTable): Players table.
            winner (bool): Winner flag.

        Returns:
        -------
            discord.Embed: Team embed.

        """
        return discord.Embed(
            title=f"{team.get('name')} players",
            description=f"```{players_table.get_string()}```",
            color=discord.Color.green() if winner else discord.Color.red(),
        )

    @abstractmethod
    async def callback(self, *args: any, **kwargs: any) -> None:
        """
        Event callback.

        Args:
        ----
            *args: Event arguments.
            **kwargs: Event keyword arguments.

        Returns:
        -------
            None

        """
        raise NotImplementedError


class EventListener:
    """Event listener for the bot."""

    def __init__(self, events: list[Event], pubsub: PubSub) -> None:
        """
        Event listener constructor.

        Args:
        ----
            events (list[Event]): List of events.
            pubsub (PubSub): Redis pubsub instance.

        Returns:
        -------
            None

        """
        self.events = events
        self.pubsub = pubsub

    async def dispatch(self, event: str, *args: any, **kwargs: any) -> None:
        """
        Dispatch event.

        Args:
        ----
            event (str): Event name.
            *args: Event arguments.
            **kwargs: Event keyword arguments.

        Returns:
        -------
            None

        """
        for e in self.events:
            if e.name == event:
                await e.callback(*args, **kwargs)

    async def listen(self) -> None:
        """Listen for events."""
        message = self.pubsub.get_message()
        while message is not None:
            if message["type"] == "pmessage":
                logger.logger.debug(f"Received message {message}")
                data = message.get("data")
                if data is None:
                    return
                data = data.decode("utf-8")
                data = json.loads(data)
                event = data.get("event")
                if not event:
                    return
                await self.dispatch(event, data)
            message = self.pubsub.get_message()
