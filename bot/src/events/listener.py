"""Event listener for the src."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

import discord
from cs2_battle_bot_api_client.api.matches import matches_retrieve
from logger import logger
from redis.client import PubSub
from schemas import Match
from settings import api_client


class Event(ABC):
    """Base class for events."""

    def __init__(self, bot: discord.Bot, name: str) -> None:
        """
        Event constructor.

        Args:
        ----
            src (discord.Bot): Bot instance.
            name (str): Event name.
            matchid (int): Match ID.

        Returns:
        -------
            None

        """
        self.bot = bot
        self.name = name

    async def move_players_to_lobby(self, match: Match) -> discord.VoiceChannel:
        """
        Move players to lobby.

        Args:
        ----
            match (Match): Match object.

        Returns:
        -------
            discord.VoiceChannel: Voice channel.

        """
        guild = self.bot.get_guild(int(match.guild.guild_id))
        channel = guild.get_channel(int(match.guild.lobby_channel))
        players = [
            guild.get_member(int(player.discord_user.user_id))
            for player in match.team1.players + match.team2.players
        ]
        logger.debug(f"Available players: {players}")
        for player in players:
            if player and player.voice:
                await player.move_to(channel)
                logger.debug(f"Moved player {player} to channel {channel}")
        return channel

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
    """Event listener for the src."""

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
                logger.debug(f"Received message {message}")
                data = message.get("data")
                if data is None:
                    return
                data = data.decode("utf-8")
                data = json.loads(data)
                event = data.get("event")
                if not event:
                    return
                logger.debug(f"Dispatching event {event}")
                match: Match = await matches_retrieve.asyncio(
                    client=api_client, id=data.get("matchid")
                )
                if not match:
                    return
                data["match"] = match.to_dict()
                await self.dispatch(event, data)
            message = self.pubsub.get_message()
