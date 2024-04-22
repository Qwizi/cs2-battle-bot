"""Going live event."""
from cs2_battle_bot_api_client.models import Match

from bot.events.listener import Event
from bot.logger import logger


class OnSeriesStartEvent(Event):
    """Series start event."""

    async def callback(self, data: dict) -> None:
        """
        On series start event callback.

        Args:
        ----
            data (dict): Event data.

        Returns:
        -------
            None

        """
        logger.debug(f"Series start event callback with data: {data}")
        match = Match.from_dict(data.get("match"))
        await self.move_players_to_lobby(match)
        message = self.bot.get_message(int(match.message_id))
        await message.reply(f"Series with match id {match.id} has started. Good luck!")


class OnSeriesEndEvent(Event):
    """Series end event."""

    async def callback(self, data: dict) -> None:
        """
        On series end event callback.

        Args:
        ----
            data (dict): Event data.

        Returns:
        -------
            None

        """
        match = Match.from_dict(data.get("match"))
        await self.move_players_to_lobby(match)
        message = self.bot.get_message(int(match.message_id))
        await message.reply(f"Series with match id {match.id} has ended. Good game!")


class OnGoingLiveEvent(Event):
    """Going live event."""

    async def callback(self, data: dict) -> None:
        """
        On going live event callback.

        Args:
        ----
            data (dict): Event data.

        Returns:
        -------
            None

        """
        logger.debug(f"Going live event callback with data: {data}")
        match = Match.from_dict(data.get("match"))
        guild = self.bot.get_guild(int(match.guild.guild_id))
        team1_channel = guild.get_channel(int(match.guild.team1_channel))
        team2_channel = guild.get_channel(int(match.guild.team2_channel))
        team1_members = [
            guild.get_member(int(player.discord_user.user_id))
            for player in match.team1.players
        ]
        team2_members = [
            guild.get_member(int(player.discord_user.user_id))
            for player in match.team2.players
        ]
        logger.debug(f"Available members in team 1: {team1_members}")
        logger.debug(f"Available members in team 2: {team2_members}")
        for member in team1_members:
            if member and member.voice:
                await member.move_to(team1_channel)
                logger.debug(f"Moved {member} to {team1_channel} channel")
        for member in team2_members:
            if member and member.voice:
                await member.move_to(team2_channel)
                logger.debug(f"Moved {member} to {team2_channel} channel")
        message = self.bot.get_message(int(match.message_id))
        await message.reply(f"Match with id {match.id} has going live. Good luck!")


class OnMapResultEvent(Event):
    """Map result event."""

    async def callback(self, data: dict) -> None:
        """
        On map result event callback.

        Args:
        ----
            data (dict): Event data.

        Returns:
        -------
            None

        """
        logger.debug(f"Map result event callback with data: {data}")
        match = Match.from_dict(data.get("match"))
        await self.move_players_to_lobby(match)
        map_number = data.get("map_number")
        map_ = match.maplist[map_number]
        num_maps = match.num_maps
        message = self.bot.get_message(int(match.message_id))
        if map_number < num_maps:
            try:
                await message.reply(
                    f"Map {map_} has ended. Good game! Next map is {match.maplist[map_number + 1]}"
                )
            except IndexError:
                await message.reply(
                    f"Map {map_} has ended. Good game! Series has ended."
                )
        else:
            await message.reply(f"Map {map_} has ended. Good game! Series has ended.")
