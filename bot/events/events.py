"""Going live event."""

from httpx import HTTPError

from bot import logger
from bot.api import get_match
from bot.events.listener import Event

MATCH_ID_IS_MISSING = "Match ID is missing"


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
        logger.logger.debug(f"Series start event callback with data: {data}")

        logger.logger.debug("Adding role to players")
        try:
            matchid = data.get("matchid")
            if not matchid:
                self.raise_match_id_error(matchid)
            match, _ = await get_match(matchid)
            await self.move_players_to_lobby_channel(match=match)
        except (HTTPError, ValueError) as exc:
            logger.logger.error(f"Error adding role to players: {exc!r}")


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
        logger.logger.debug(f"Series end event callback with data: {data}")

        logger.logger.debug("Removing role from players")
        try:
            matchid = data.get("matchid")
            if not matchid:
                self.raise_match_id_error(matchid)
            match, _ = await get_match(matchid)
        except (HTTPError, ValueError) as exc:
            logger.logger.error(f"Error removing role from players: {exc!r}")


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
        logger.logger.debug(f"Map result event callback with data: {data}")

        logger.logger.debug("Moving players to teams voice channels")
        try:
            matchid = data.get("matchid")
            if not matchid:
                self.raise_match_id_error(matchid)
            match, _ = await get_match(matchid)
            await self.move_players_to_lobby_channel(match=match)
        except (HTTPError, ValueError) as exc:
            logger.logger.error(f"Error moving players to teams: {exc!r}")


class OnRoundEndEvent(Event):
    """Round end event."""

    async def callback(self, data: dict) -> None:
        """
        On round end event callback.

        Args:
        ----
            data (dict): Event data.

        Returns:
        -------
            None

        """
        logger.logger.debug(f"Round end event callback with data: {data}")

        logger.logger.debug("Moving players to teams voice channels")
        try:
            matchid = data.get("matchid")
            if not matchid:
                self.raise_match_id_error(matchid)
            match, _ = await get_match(matchid)
            winner = data.get("winner")
            team1 = data.get("team1")
            team2 = data.get("team2")
            team1_players = team1.get("players")
            team2_players = team2.get("players")

            team1_players_table = self.create_players_table(team1_players)
            team2_players_table = self.create_players_table(team2_players)

            team1_stats_embed = await self.create_team_stats_embed(
                team1,
                team1_players_table,
                winner=winner.get("team") == "team1",
            )
            team2_stats_embed = await self.create_team_stats_embed(
                team2,
                team2_players_table,
                winner=winner.get("team") == "team2",
            )
            message = self.bot.get_message(match.message_id)
            message_embed = message.embeds[0]
            logger.logger.debug(f"Message: {message}")
            await message.edit(
                embeds=[message_embed, team1_stats_embed, team2_stats_embed]
            )
        except (HTTPError, ValueError) as exc:
            logger.logger.error(f"Error moving players to teams: {exc!r}")


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
        logger.logger.debug(f"Going live event callback with data: {data}")

        logger.logger.debug("Moving players to teams voice channels")
        try:
            matchid = data.get("matchid")
            if not matchid:
                self.raise_match_id_error(matchid)
            match, _ = await get_match(matchid)
            await self.move_players_to_teams_channel(match=match)
        except (HTTPError, ValueError) as exc:
            logger.logger.error(f"Error moving players to teams: {exc!r}")
