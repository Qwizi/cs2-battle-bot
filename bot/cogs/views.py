from __future__ import annotations

from abc import ABC, abstractmethod

import discord
import httpx

from bot.api import (
    ban_map,
    get_curent_match,
    get_match_map_bans,
    get_match_map_picks,
    load_match,
    pick_map,
    recreate_match,
    shuffle_teams,
)
from bot.cogs.utils import (
    update_match_embed_with_maps,
)
from bot.schemas import CreateBanMap, CreatePickMap, Match
from bot.settings import settings


class MapView(ABC, discord.ui.View):
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
            title (str): Title of the view.
            options (list[discord.SelectOption]): List of select options.

        """
        super().__init__()
        self.select = discord.ui.Select(
            placeholder=title if title else "Wybierz mape do zbanowania",
            options=options,
        )
        self.select.callback = self.map_select_callback
        self.add_item(self.select)
        self.match = match

    @discord.ui.button(
        label="Przelosuj druzyny", style=discord.ButtonStyle.secondary, emoji="🔄"
    )
    async def shuffle_teams_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
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
                "Tylko autor komendy moze wykonac ta akcje", ephemeral=True
            )
            return
        try:
            updated_match, _ = await shuffle_teams(self.match.id)

        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        updated_match_embed = updated_match.create_match_embed(interaction.user.id)
        map_select_options = [
            discord.SelectOption(label=tag, value=tag)
            for tag in updated_match.get_maps_tags()
        ]
        map_select_view = MapBanView(
            options=map_select_options,
            match=updated_match,
        )
        await interaction.edit(embed=updated_match_embed, view=map_select_view)

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
            match match.type:
                case "BO1":
                    await self.bo1_map_ban_logic(interaction, match, map_tag)
                case "BO3":
                    await self.bo3_map_ban_logic(interaction, match, map_tag)
        except httpx.HTTPError as e:
            print(repr(e))
            await interaction.followup.send("Failed to ban map", ephemeral=True)

    async def bo1_map_ban_logic(
        self,
        interaction: discord.Interaction,
        match: Match,
        map_tag: str,
    ) -> None:
        team_leaders = match.get_teams_leaders()
        map_bans, _ = await get_match_map_bans(match.id)

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

        try:
            # Perform map ban actions
            updated_match, _ = await ban_map(
                data=CreateBanMap(
                    match_id=match.id,
                    team_id=match.team1.id
                    if banning_team_leader == team_leaders[0]
                    else match.team2.id,
                    map_tag=map_tag,
                )
            )
            await interaction.followup.send(
                f"{banning_team_leader.mention_user()} zbanowal mape {map_tag}"
            )

            maps_left = len(updated_match.maps)

            # Update match view or launch match
            if maps_left == 1:
                launch_match_view = LaunchMatchView()
                await interaction.message.edit(
                    embed=update_match_embed_with_maps(
                        interaction.message.embeds[0],
                        updated_match.get_maps_tags(),
                        interaction.user.id,
                    ),
                    view=launch_match_view,
                )
            else:
                await interaction.message.edit(
                    view=MapBanView(
                        title=f"Teraz banuje {team_leaders[1 - team_leaders.index(banning_team_leader)].discord_user.username}",
                        options=[
                            discord.SelectOption(label=tag, value=tag)
                            for tag in updated_match.get_maps_tags()
                        ],
                        match=updated_match,
                    )
                )
        except Exception as e:  # Add error handling for unexpected issues
            print(f"Error during map ban: {e!r}")
            await interaction.user.send(
                "An error occurred during the map ban process. Please try again or contact support."
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
        map_bans, _ = await get_match_map_bans(match.id)
        map_bans_count = map_bans.count
        # Determine the current banning team and leader
        if (
            not settings.TESTING
        ):  # Prioritize interaction user's team in non-testing mode
            banning_team_leader = (
                team_leaders[0]
                if interaction.user.id == team_leaders[0].discord_user.user_id
                else team_leaders[1]
            )
        else:  # Handle testing mode logic
            if map_bans.count > 0:
                last_banning_team = map_bans.results[0].team
                banning_team_leader = (
                    team_leaders[1]
                    if last_banning_team == match.team1
                    else team_leaders[0]
                )
            else:  # Start with team1 in testing mode if no bans yet
                banning_team_leader = team_leaders[0]

        try:
            # Perform map ban actions
            updated_match, _ = await ban_map(
                data=CreateBanMap(
                    match_id=match.id,
                    team_id=match.team1.id
                    if banning_team_leader == team_leaders[0]
                    else match.team2.id,
                    map_tag=map_tag,
                )
            )
            await interaction.followup.send(
                f"{banning_team_leader.mention_user()} zbanowal mape {map_tag}"
            )
            map_pick_tags = [map_pick.map.tag for map_pick in updated_match.map_picks]
            maps_left = [
                map.tag for map in updated_match.maps if map.tag not in map_pick_tags
            ]
            map_bans_count = len(updated_match.map_bans)
            left_maps = len(updated_match.maps)
            if map_bans_count == 2:
                await interaction.message.edit(
                    view=MapPickView(
                        title=f"Teraz wybiera {team_leaders[1 - team_leaders.index(banning_team_leader)].discord_user.username}",
                        options=[
                            discord.SelectOption(label=tag, value=tag)
                            for tag in maps_left
                        ],
                        match=updated_match,
                    )
                )
            else:
                await interaction.message.edit(
                    view=MapBanView(
                        title=f"Teraz banuje {team_leaders[1 - team_leaders.index(banning_team_leader)].discord_user.username}",
                        options=[
                            discord.SelectOption(label=tag, value=tag)
                            for tag in maps_left
                        ],
                        match=updated_match,
                    )
                )
            if left_maps == 3:
                launch_match_view = LaunchMatchView()
                await interaction.message.edit(
                    embed=update_match_embed_with_maps(
                        interaction.message.embeds[0],
                        updated_match.get_maps_tags(),
                        interaction.user.id,
                    ),
                    view=launch_match_view,
                )
        except Exception as e:  # Add error handling for unexpected issues
            print(f"Error during map ban: {e!r}")
            await interaction.user.send(
                "An error occurred during the map ban process. Please try again or contact support."
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
            await self.map_pick_logic(interaction, self.match, map_tag)
        except httpx.HTTPError as e:
            print(repr(e))
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
        map_picks, _ = await get_match_map_picks(match.id)
        try:
            # Determine the current banning team and leader
            if (
                not settings.TESTING
            ):  # Prioritize interaction user's team in non-testing mode
                banning_team_leader = (
                    team_leaders[0]
                    if interaction.user.id == team_leaders[0].discord_user.user_id
                    else team_leaders[1]
                )
            else:  # Handle testing mode logic
                if map_picks.count > 0:
                    last_banning_team = map_picks.results[0].team
                    banning_team_leader = (
                        team_leaders[1]
                        if last_banning_team == match.team1
                        else team_leaders[0]
                    )
                else:  # Start with team1 in testing mode if no bans yet
                    banning_team_leader = team_leaders[0]
            updated_match, _ = await pick_map(
                data=CreatePickMap(
                    match_id=match.id,
                    team_id=match.team1.id
                    if banning_team_leader == team_leaders[0]
                    else match.team2.id,
                    map_tag=map_tag,
                )
            )
            await interaction.followup.send(
                f"{banning_team_leader.mention_user()} wybral mape {map_tag}"
            )
            map_pick_tags = [map_pick.map.tag for map_pick in updated_match.map_picks]
            maps_left = [
                map.tag for map in updated_match.maps if map.tag not in map_pick_tags
            ]
            map_picks_count = len(updated_match.map_picks)
            if map_picks_count == 2:
                await interaction.message.edit(
                    view=MapBanView(
                        title=f"Teraz banuje {team_leaders[1 - team_leaders.index(banning_team_leader)].discord_user.username}",
                        options=[
                            discord.SelectOption(label=tag, value=tag)
                            for tag in maps_left
                        ],
                        match=updated_match,
                    )
                )
            else:
                await interaction.message.edit(
                    view=MapPickView(
                        title=f"Teraz wybiera {team_leaders[1 - team_leaders.index(banning_team_leader)].discord_user.username}",
                        options=[
                            discord.SelectOption(label=tag, value=tag)
                            for tag in maps_left
                        ],
                        match=updated_match,
                    )
                )
        except Exception as e:  # Add error handling for unexpected issues
            print(f"Error during map pick: {e!r}")
            await interaction.user.send(
                "An error occurred during the map pick process. Please try again or contact support."
            )


class LaunchMatchView(discord.ui.View):
    """Launch match view."""

    @discord.ui.button(label="Start!", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_match_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Start match button callback.

        Args:
        ----
            self (LaunchMatchView): LaunchMatchView object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                "Tylko autor komendy moze wykonac ta akcje", ephemeral=True
            )
            return
        try:
            await load_match()
        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        else:
            await interaction.followup.send("Pomyślnie załadowano mecz!")

    @discord.ui.button(label="Recreate", style=discord.ButtonStyle.danger, emoji="🔄")
    async def recreate_match_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Recreate match button callback.

        Args:
        ----
            self (LaunchMatchView): LaunchMatchView object.
            interaction (discord.Interaction): Interaction object.

        Returns:
        -------
            None

        """
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                "Tylko autor komendy moze wykonac ta akcje", ephemeral=True
            )
            return
        try:
            current_match, _ = await get_curent_match()
            match, _ = await recreate_match(current_match.matchid)
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
