"""Match views."""

from __future__ import annotations

from abc import ABC, abstractmethod

import discord
import httpx
from discord.ui.item import Item  # noqa: TCH002

from bot import logger
from bot.api import (
    ban_map,
    get_curent_match,
    get_match_map_bans,
    get_match_map_picks,
    join_match,
    load_match,
    pick_map,
    recreate_match,
    shuffle_teams,
)
from bot.cogs.utils import (
    update_match_embed_with_maps,
)
from bot.i18n import _
from bot.schemas import CreateBanMap, CreatePickMap, Match
from bot.settings import settings


class MapView(ABC, discord.ui.View):
    """Map view."""

    def __init__(
        self,
        options: list[discord.SelectOption],
        match: Match,
        title: str | None = None,
    ) -> None:
        """
        Initialize map ban view.

        Args:
        ----
            options (list[discord.SelectOption]): Options.
            match (Match): Match object.
            title (str, optional): Title. Defaults to None.

        """
        super().__init__()
        self.select = discord.ui.Select(
            placeholder=title if title else _("chose_map_to_ban"),
            options=options,
        )
        self.select.callback = self.map_select_callback
        self.add_item(self.select)
        self.match = match

        self.create_buttons()

    def create_buttons(self) -> None:
        """
        Create buttons.

        Args:
        ----
            self (MapView): MapView object.

        Returns:
        -------
            None

        """
        self.shuffle_button = discord.ui.Button(
            label=_("shuffle_teams"),
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
        )
        self.shuffle_button.callback = self.shuffle_teams_button_callback
        self.add_item(self.shuffle_button)

        self.player_join_match_button = discord.ui.Button(
            label=_("join_to_match"),
            style=discord.ButtonStyle.secondary,
            emoji="🎮",
        )
        self.player_join_match_button.callback = self.player_join_match_button_callback
        self.add_item(self.player_join_match_button)

    async def shuffle_teams_button_callback(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Shuffle teams button callback.

        Args:
        ----
            self (ShuffleTeamsButton): ShuffleTeamsButton object.
            button (discord.ui.Button): Button object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                _("error_user_is_no_author_of_match"), ephemeral=True
            )
            return
        try:
            updated_match, _response = await shuffle_teams(self.match.id)

        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        updated_match_embed = updated_match.create_match_embed()
        map_select_options = [
            discord.SelectOption(label=tag, value=tag)
            for tag in updated_match.get_maps_tags()
        ]
        map_select_view = MapBanView(
            options=map_select_options,
            match=updated_match,
        )
        await interaction.edit(embed=updated_match_embed, view=map_select_view)

    async def player_join_match_button_callback(
        self, interaction: discord.Interaction
    ) -> None:
        """
        Player join match button callback.

        Args:
        ----
            self (PlayerJoinMatchButton): PlayerJoinMatchButton object.
            button (discord.ui.Button): Button object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        try:
            current_match, _response = await get_curent_match()
            updated_match, _response2 = await join_match(
                current_match.matchid, interaction.user.id
            )

            await interaction.followup.send(
                _("user_joined_match", interaction.user.mention)
            )
            updated_match_embed = updated_match.create_match_embed()
            await interaction.edit(embed=updated_match_embed)
        except (httpx.HTTPError, httpx.HTTPStatusError) as e:
            if e.response.status_code == httpx.codes.BAD_REQUEST:
                logger.logger.error(e.response.json())
            logger.logger.error(f"Error during match join: {e!r}")
            await interaction.followup.send("Failed to join a match", ephemeral=True)

    @abstractmethod
    async def map_select_callback(self, interaction: discord.Interaction) -> None:
        """
        Map select callback.

        Args:
        ----
            self (MapBanBO1View): MapBanBO1View object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        raise NotImplementedError


class MapBanView(MapView):
    """Map ban view."""

    async def map_select_callback(self, interaction: discord.Interaction) -> None:
        """
        BO1 map ban callback.

        Args:
        ----
            self (MapBanBO1View): MapBanBO1View object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        try:
            await interaction.response.defer()
            match = self.match
            map_tag = interaction.data["values"][0]
            if not self.match.check_user_is_in_teams(interaction.user.id):
                await interaction.followup.send(
                    _("error_user_is_not_in_match"), ephemeral=True
                )
                return
            if not self.match.check_user_is_leader_in_teams(interaction.user.id):
                await interaction.followup.send(
                    _("error_user_is_not_leader"), ephemeral=True
                )
                return
            match match.type:
                case "BO1":
                    await self.bo1_map_ban_logic(interaction, match, map_tag)
                case "BO3":
                    await self.bo3_map_ban_logic(interaction, match, map_tag)
        except (httpx.HTTPError, httpx.HTTPStatusError) as e:
            logger.logger.error(f"Error during map ban: {e!r}")
            if e.response and e.response.status_code == httpx.codes.BAD_REQUEST:
                error_json = e.response.json()
                error_message = error_json.get("message")
                logger.logger.error(e.response.json())
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await interaction.followup.send("Failed to ban map", ephemeral=True)

    async def bo1_map_ban_logic(
        self,
        interaction: discord.Interaction,
        match: Match,
        map_tag: str,
    ) -> None:
        """
        BO1 map ban logic.

        Args:
        ----
            self (MapBanView): MapBanView object.
            interaction (discord.Interaction): Interaction object.
            match (Match): Match object.
            map_tag (str): Map tag.

        Returns:
        -------
            None

        """
        team_leaders = match.get_teams_leaders()
        map_bans, _response = await get_match_map_bans(match.id)

        # Determine the current banning team and leader
        if (
            not settings.TESTING
        ):  # Prioritize interaction user's team in non-testing mode
            banning_team_leader = (
                team_leaders[0]
                if interaction.user.id == team_leaders[0].discord_user.user_id
                else team_leaders[1]
            )
        elif map_bans.count > 0:
            last_banning_team = map_bans.results[0].team
            banning_team_leader = (
                team_leaders[1] if last_banning_team == match.team1 else team_leaders[0]
            )
        else:  # Start with team1 in testing mode if no bans yet
            banning_team_leader = team_leaders[0]

        # Perform map ban actions
        updated_match, _response = await ban_map(
            data=CreateBanMap(
                match_id=match.id,
                team_id=match.team1.id
                if banning_team_leader == team_leaders[0]
                else match.team2.id,
                map_tag=map_tag,
            )
        )
        await interaction.followup.send(
            _("user_banned_map", banning_team_leader.mention_user(), map_tag)
        )

        maps_left = len(updated_match.maps)
        logger.logger.debug(
            f"User {interaction.user.id} banned map {map_tag} in match {match.id} of type {match.type}. Maps left: {maps_left}. Team1: {match.team1.id}. Team2: {match.team2.id}. Banning team leader: {banning_team_leader.discord_user.user_id}. Team leaders: {team_leaders[0].discord_user.user_id}, {team_leaders[1].discord_user.user_id}."
        )
        # Update match view or launch match
        if maps_left == 1:
            await self.launch_match(updated_match, interaction)
        else:
            await interaction.message.edit(
                view=MapBanView(
                    title=_(
                        "user_is_banning",
                        team_leaders[
                            1 - team_leaders.index(banning_team_leader)
                        ].discord_user.username,
                    ),
                    options=[
                        discord.SelectOption(label=tag, value=tag)
                        for tag in updated_match.get_maps_tags()
                    ],
                    match=updated_match,
                )
            )

    async def bo3_map_ban_logic(
        self,
        interaction: discord.Interaction,
        match: Match,
        map_tag: str,
    ) -> None:
        """
        Map ban logic for BO3 matches.

        Args:
        ----
            self (MapBanView): MapBanView object.
            interaction (discord.Interaction): Interaction object.
            match (Match): Match object.
            map_tag (str): Map tag.

        Returns:
        -------
            None

        """
        team_leaders = match.get_teams_leaders()
        map_bans, _response = await get_match_map_bans(match.id)
        map_bans_count = map_bans.count
        map_bans_required_to_pick = 2
        maps_left_to_launch = 3
        # Determine the current banning team and leader
        if (
            not settings.TESTING
        ):  # Prioritize interaction user's team in non-testing mode
            banning_team_leader = (
                team_leaders[0]
                if interaction.user.id == team_leaders[0].discord_user.user_id
                else team_leaders[1]
            )
        elif map_bans.count > 0:  # Handle testing mode logic
            last_banning_team = map_bans.results[0].team
            banning_team_leader = (
                team_leaders[1] if last_banning_team == match.team1 else team_leaders[0]
            )
        else:  # Start with team1 in testing mode if no bans yet
            banning_team_leader = team_leaders[0]

        if interaction.user.id == team_leaders[0].discord_user.user_id:
            team_id = match.team1.id
        else:
            team_id = match.team2.id

            # Perform map ban actions
        updated_match, _response = await ban_map(
            data=CreateBanMap(
                match_id=match.id,
                team_id=team_id
                if banning_team_leader == team_leaders[0]
                else match.team2.id,
                map_tag=map_tag,
            )
        )
        await interaction.followup.send(
            _("user_ban_map", banning_team_leader.mention_user(), map_tag)
        )
        map_pick_tags = [map_pick.map.tag for map_pick in updated_match.map_picks]
        maps_left = [
            _map.tag for _map in updated_match.maps if _map.tag not in map_pick_tags
        ]
        map_bans_count = len(updated_match.map_bans)
        left_maps = len(updated_match.maps)
        if map_bans_count == map_bans_required_to_pick:
            await interaction.message.edit(
                view=MapPickView(
                    title=_(
                        "user_is_picking",
                        team_leaders[
                            1 - team_leaders.index(banning_team_leader)
                        ].discord_user.username,
                    ),
                    options=[
                        discord.SelectOption(label=tag, value=tag) for tag in maps_left
                    ],
                    match=updated_match,
                )
            )
        else:
            await interaction.message.edit(
                view=MapBanView(
                    title=_(
                        "user_is_banning",
                        team_leaders[
                            1 - team_leaders.index(banning_team_leader)
                        ].discord_user.username,
                    ),
                    options=[
                        discord.SelectOption(label=tag, value=tag) for tag in maps_left
                    ],
                    match=updated_match,
                )
            )
        if left_maps == maps_left_to_launch:
            current_match, _response = await get_curent_match()
            launch_match_view = LaunchMatchView()
            await interaction.message.edit(
                embed=update_match_embed_with_maps(
                    interaction.message.embeds[0],
                    current_match.maplist,
                ),
                view=launch_match_view,
            )

    async def launch_match(
        self, match: Match, interaction: discord.Interaction
    ) -> None:
        """
        Launch match.

        Args:
        ----
            self (MapBanView): MapBanView object.
            match (Match): Match object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        launch_match_view = LaunchMatchView()
        await interaction.message.edit(
            embed=update_match_embed_with_maps(
                interaction.message.embeds[0],
                match.get_maps_tags(),
            ),
            view=launch_match_view,
        )


class MapPickView(MapView):
    """Map pick view."""

    async def map_select_callback(self, interaction: discord.Interaction) -> None:
        """
        Map select callback.

        Args:
        ----
            self (MapPickView): MapPickView object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        try:
            await interaction.response.defer()
            map_tag = interaction.data["values"][0]

            if not self.match.check_user_is_in_teams(interaction.user.id):
                await interaction.followup.send(
                    _("error_user_is_not_in_match"), ephemeral=True
                )
                return
            if not self.match.check_user_is_leader_in_teams(interaction.user.id):
                await interaction.followup.send(
                    _("error_user_is_not_leader"), ephemeral=True
                )
                return
            await self.map_pick_logic(interaction, self.match, map_tag)
        except (httpx.HTTPError, httpx.HTTPStatusError) as e:
            logger.logger.error(f"Error during map pick: {e!r}")
            if e.response and e.response.status_code == httpx.codes.BAD_REQUEST:
                error_json = e.response.json()
                error_message = error_json.get("message")
                logger.logger.error(e.response.json())
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await interaction.followup.send("Failed to pick map", ephemeral=True)

    async def map_pick_logic(
        self,
        interaction: discord.Interaction,
        match: Match,
        map_tag: str,
    ) -> None:
        """
        Map pick logic.

        Args:
        ----
            self (MapPickView): MapPickView object.
            interaction (discord.Interaction): Interaction object.
            match (Match): Match object.
            map_tag (str): Map tag.

        Returns:
        -------
            None

        """
        team_leaders = match.get_teams_leaders()
        map_picks, _response = await get_match_map_picks(match.id)
        # Determine the current banning team and leader
        if (
            not settings.TESTING
        ):  # Prioritize interaction user's team in non-testing mode
            banning_team_leader = (
                team_leaders[0]
                if interaction.user.id == team_leaders[0].discord_user.user_id
                else team_leaders[1]
            )
        elif map_picks.count > 0:
            last_banning_team = map_picks.results[0].team
            banning_team_leader = (
                team_leaders[1] if last_banning_team == match.team1 else team_leaders[0]
            )
        else:  # Start with team1 in testing mode if no bans yet
            banning_team_leader = team_leaders[0]

        if interaction.user.id == team_leaders[0].discord_user.user_id:
            team_id = match.team1.id
        else:
            team_id = match.team2.id
        updated_match, _response = await pick_map(
            data=CreatePickMap(
                match_id=match.id,
                team_id=team_id
                if banning_team_leader == team_leaders[0]
                else match.team2.id,
                map_tag=map_tag,
            )
        )
        await interaction.followup.send(
            _("user_pick_map", banning_team_leader.mention_user(), map_tag)
        )
        map_pick_tags = [map_pick.map.tag for map_pick in updated_match.map_picks]
        maps_left = [
            _map.tag for _map in updated_match.maps if _map.tag not in map_pick_tags
        ]
        map_picks_count = len(updated_match.map_picks)
        if map_picks_count == 2:  # noqa: PLR2004
            await interaction.message.edit(
                view=MapBanView(
                    title=_(
                        "user_is_banning",
                        team_leaders[
                            1 - team_leaders.index(banning_team_leader)
                        ].discord_user.username,
                    ),
                    options=[
                        discord.SelectOption(label=tag, value=tag) for tag in maps_left
                    ],
                    match=updated_match,
                )
            )
        else:
            await interaction.message.edit(
                view=MapPickView(
                    title=_(
                        "user_is_picking",
                        team_leaders[
                            1 - team_leaders.index(banning_team_leader)
                        ].discord_user.username,
                    ),
                    options=[
                        discord.SelectOption(label=tag, value=tag) for tag in maps_left
                    ],
                    match=updated_match,
                )
            )


class LaunchMatchView(discord.ui.View):
    """Launch match view."""

    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
    ) -> None:
        """
        Launch match view.

        Args:
        ----
            items (Item): Items.
            timeout (float, optional): Timeout. Defaults to 180.
            disable_on_timeout (bool, optional): Disable on timeout. Defaults to False.

        Returns:
        -------
            None

        """
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        join_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Dolacz do serwera",
            emoji="🎮",
            url="http://localhost:8002/accounts/join/"
            if settings.TESTING
            else f"{settings.API_URL}/accounts/join/",
        )
        self.add_item(join_btn)

    @discord.ui.button(label="Start!", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_match_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Start match button callback.

        Args:
        ----
            self (LaunchMatchView): LaunchMatchView object.
            button (discord.ui.Button): Button object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                _("error_user_is_no_author_of_match"), ephemeral=True
            )
            return
        try:
            match, _response = await load_match()

            message_id = interaction.message.id
            logger.logger.debug(f"Message id {message_id}")
            logger.logger.debug(
                f"Match {match.id} started by user {interaction.user.id}"
            )
        except httpx.HTTPError as e:
            logger.logger.debug(f"Error during match load: {e!r}")
            if e.response and e.response.status_code == httpx.codes.BAD_REQUEST:
                logger.logger.debug(e.response.json())
                await interaction.followup.send(
                    "Mecz zostal juz zaladowany", ephemeral=True
                )
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        else:
            await interaction.followup.send(_("success_match_loaded"))

    @discord.ui.button(label="Recreate", style=discord.ButtonStyle.danger, emoji="🔄")
    async def recreate_match_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Recreate match button callback.

        Args:
        ----
            self (LaunchMatchView): LaunchMatchView object.
            button (discord.ui.Button): Button object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                _("error_user_is_no_author_of_match"), ephemeral=True
            )
            return
        try:
            current_match, _response = await get_curent_match()
            match, _response2 = await recreate_match(current_match.matchid)
            map_select_options = [
                discord.SelectOption(label=tag, value=tag)
                for tag in match.get_maps_tags()
            ]
            map_select_view = MapBanView(
                options=map_select_options,
                match=match,
            )
            await interaction.edit(view=map_select_view)

        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )


class ShuffleTeamsView(discord.ui.View):
    """Shuffle teams view."""
