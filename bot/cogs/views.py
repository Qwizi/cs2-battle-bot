"""Match views."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

import discord
from anyio import Path
from cs2_battle_bot_api_client.api.guilds import guilds_update
from cs2_battle_bot_api_client.api.matches import (
    matches_ban_create,
    matches_load_create,
    matches_pick_create,
    matches_retrieve,
)
from cs2_battle_bot_api_client.errors import UnexpectedStatus
from cs2_battle_bot_api_client.models import Match
from cs2_battle_bot_api_client.models.guild import Guild
from cs2_battle_bot_api_client.models.match_ban_map import MatchBanMap
from cs2_battle_bot_api_client.models.match_ban_map_result import MatchBanMapResult
from cs2_battle_bot_api_client.models.match_pick_map import MatchPickMap
from cs2_battle_bot_api_client.models.match_pick_map_result import MatchPickMapResult
from cs2_battle_bot_api_client.models.type_enum import TypeEnum
from cs2_battle_bot_api_client.models.update_guild import UpdateGuild
from cs2_battle_bot_api_client.types import Response
from discord.ui.item import Item
from httpx import URL

from bot import logger
from bot.cogs.utils import create_match_embed
from bot.i18n import _
from bot.settings import api_client, settings


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
        await interaction.response.defer()
        match = self.match
        map_tag = interaction.data["values"][0]
        match match.type:
            case TypeEnum.BO1:
                await self.bo1_map_ban_logic(interaction, match, map_tag)
            case TypeEnum.BO3:
                await self.bo3_map_ban_logic(interaction, match, map_tag)

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
        interaction_user_id = (
            interaction.user.id
            if not settings.DEBUG
            else match.team1.leader.discord_user.user_id
            if len(match.map_bans) == 0
            else match.team1.leader.discord_user.user_id
            if match.last_map_ban.team == match.team2
            else match.team2.leader.discord_user.user_id
        )

        try:
            response: Response[
                MatchBanMapResult
            ] = await matches_ban_create.asyncio_detailed(
                client=api_client,
                id=match.id,
                body=MatchBanMap(
                    interaction_user_id=interaction_user_id, map_tag=map_tag
                ),
            )
        except UnexpectedStatus as err:
            try:
                data = json.loads(err.content.decode(encoding="utf-8"))
            except json.JSONDecodeError:
                data = err.content.decode(encoding="utf-8")
            await interaction.followup.send(data)
            return

        await interaction.followup.send(
            _("user_ban_map", f"<@{interaction_user_id}>", map_tag)
        )

        ban_result = response.parsed
        updated_match = await matches_retrieve.asyncio(client=api_client, id=match.id)
        match_embed = create_match_embed(updated_match)
        view = (
            LaunchMatchView(timeout=None, match=updated_match)
            if len(ban_result.maps_left) == 1
            else MapBanView(
                title=_(
                    "user_is_banning",
                    ban_result.next_ban_team.leader.discord_user.username,
                ),
                options=[
                    discord.SelectOption(label=tag, value=tag)
                    for tag in ban_result.maps_left
                ],
                match=updated_match,
            )
        )

        await interaction.message.edit(embed=match_embed, view=view)

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
        interaction_user_id = (
            interaction.user.id
            if not settings.DEBUG
            else match.team1.leader.discord_user.user_id
            if len(match.map_bans) == 0
            else match.team1.leader.discord_user.user_id
            if match.last_map_ban.team == match.team2
            else match.team2.leader.discord_user.user_id
        )

        try:
            response = await matches_ban_create.asyncio_detailed(
                client=api_client,
                id=match.id,
                body=MatchBanMap(
                    interaction_user_id=interaction_user_id, map_tag=map_tag
                ),
            )
        except UnexpectedStatus as err:
            await interaction.followup.send(
                json.loads(err.content.decode(encoding="utf-8"))["message"]
            )
            return

        await interaction.followup.send(
            _("user_ban_map", f"<@{interaction_user_id}>", map_tag)
        )

        ban_result = response.parsed
        updated_match = await matches_retrieve.asyncio(client=api_client, id=match.id)
        match_embed = create_match_embed(updated_match)
        if len(updated_match.maplist) == 3:
            view = LaunchMatchView(timeout=None, match=updated_match)
        elif ban_result.map_bans_count == 2 and len(updated_match.map_picks) < 2:
            view = MapPickView(
                title=_(
                    "user_is_picking",
                    ban_result.next_ban_team.leader.discord_user.username,
                ),
                options=[
                    discord.SelectOption(label=tag, value=tag)
                    for tag in ban_result.maps_left
                ],
                match=updated_match,
            )
        else:
            view = MapBanView(
                title=_(
                    "user_is_banning",
                    ban_result.next_ban_team.leader.discord_user.username,
                ),
                options=[
                    discord.SelectOption(label=tag, value=tag)
                    for tag in ban_result.maps_left
                ],
                match=updated_match,
            )

        await interaction.message.edit(embed=match_embed, view=view)


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
        await interaction.response.defer()
        match = self.match
        map_tag = interaction.data["values"][0]

        interaction_user_id = (
            interaction.user.id
            if not settings.DEBUG
            else match.team1.leader.discord_user.user_id
            if len(match.map_picks) == 0
            else match.team1.leader.discord_user.user_id
            if match.last_map_pick.team == match.team2
            else match.team2.leader.discord_user.user_id
        )

        try:
            response: Response[
                MatchPickMapResult
            ] = await matches_pick_create.asyncio_detailed(
                client=api_client,
                id=match.id,
                body=MatchPickMap(
                    interaction_user_id=interaction_user_id, map_tag=map_tag
                ),
            )
        except UnexpectedStatus as err:
            await interaction.followup.send(
                json.loads(err.content.decode(encoding="utf-8"))["message"]
            )
            return

        await interaction.followup.send(
            _("user_pick_map", f"<@{interaction_user_id}>", map_tag)
        )

        pick_result = response.parsed

        updated_match = await matches_retrieve.asyncio(client=api_client, id=match.id)

        await interaction.message.edit(
            view=MapPickView(
                title=_(
                    "user_is_picking",
                    pick_result.next_pick_team.leader.discord_user.username,
                ),
                options=[
                    discord.SelectOption(label=map, value=map)
                    for map in pick_result.maps_left
                ],
                match=updated_match,
            )
            if pick_result.map_picks_count < 2
            else MapBanView(
                title=_(
                    "user_is_banning",
                    pick_result.next_pick_team.leader.discord_user.username,
                ),
                options=[
                    discord.SelectOption(label=map, value=map)
                    for map in pick_result.maps_left
                ],
                match=updated_match,
            )
        )


class LaunchMatchView(discord.ui.View):
    """Launch match view."""

    def __init__(
        self,
        *items: Item,
        timeout: float | None = None,
        disable_on_timeout: bool = False,
        match: Match,
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
        if match.server:
            url = URL(url=match.server.join_url)
            if settings.DEBUG:
                url = url.copy_with(scheme="http", host="localhost", port=8002)
            join_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label=_("connect_to_server"),
                emoji="🎮",
                url=str(url),
            )
            self.add_item(join_btn)
        self.match = match

    @discord.ui.button(
        label="Start!",
        custom_id="start-button",
        style=discord.ButtonStyle.primary,
        emoji="🚀",
    )
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
        if interaction.user.id != int(self.match.author.user_id):
            await interaction.followup.send(
                _("error_user_is_no_author_of_match"), ephemeral=True
            )
            return
        config_dict = self.match.config.to_dict()
        config_string = json.dumps(config_dict, indent=4, sort_keys=False)
        config_filename = (
            Path(__file__).parent.parent
            / "temp"
            / f"match_{config_dict['matchid']}.json"
        )
        async with Path(config_filename).open("w") as f:
            await f.write(config_string)
        file = discord.File(config_filename)
        await Path.unlink(config_filename)
        if self.match.server is None:
            await interaction.followup.send(
                _("success_match_loaded_without_server", self.match.load_match_command),
                ephemeral=True,
                file=file,
            )
        else:
            try:
                await matches_load_create.asyncio_detailed(
                    client=api_client, id=self.match.id, body=self.match
                )
            except UnexpectedStatus as err:
                await interaction.followup.send(
                    json.loads(err.content.decode(encoding="utf-8"))["message"]
                )
                return
            await interaction.followup.send(
                f"""
               Mecz zostal zaladowany na serwerze {self.match.server.name}
                """,
                ephemeral=True,
                file=file,
            )


class ConfigureGuildView(discord.ui.View):
    """Configure guild view."""

    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        guild: Guild,
    ) -> None:
        """
        Configure guild view.

        Args:
        ----
                items (Item): Items.
                timeout (float, optional): Timeout. Defaults to 180.
                disable_on_timeout (bool, optional): Disable on timeout. Defaults to False.
                guild_id (str): Guild ID.

        Returns:
        -------
                None

        """
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.guild = guild

    @discord.ui.channel_select(
        placeholder="Wybierz kanal dla lobby", channel_types=[discord.ChannelType.voice]
    )
    async def configure_lobby_channel(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        """
        Configure guild button callback.

        Args:
        ----
                self (ConfigureGuildView): ConfigureGuildView object.
                button (discord.ui.Button): Button object.
                interaction (discord.Interaction): Interaction object.

        Returns:
        -------
                None

        """
        await interaction.response.defer()
        channel = select.values[0]
        await interaction.followup.send(
            f"Kanal lobby ustawiony na {channel}", ephemeral=True
        )

        response: Response[Guild] = await guilds_update.asyncio_detailed(
            client=api_client,
            guild_id=self.guild.guild_id,
            body=UpdateGuild(lobby_channel=channel.id),
        )
        updated_guild = response.parsed

        logger.logger.debug(f"Updated guild: {updated_guild}")

    @discord.ui.channel_select(
        placeholder="Wybierz kanal dla Team1", channel_types=[discord.ChannelType.voice]
    )
    async def configure_team1_channel(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        """
        Configure guild button callback.

        Args:
        ----
                self (ConfigureGuildView): ConfigureGuildView object.
                button (discord.ui.Button): Button object.
                interaction (discord.Interaction): Interaction object.

        Returns:
        -------
                None

        """
        await interaction.response.defer()
        channel = select.values[0]
        await interaction.followup.send(
            f"Kanal dla druzyny Team 1 ustawiony na {channel}", ephemeral=True
        )

        response: Response[Guild] = await guilds_update.asyncio_detailed(
            client=api_client,
            guild_id=self.guild.guild_id,
            body=UpdateGuild(team1_channel=channel.id),
        )
        updated_guild = response.parsed

        logger.logger.debug(f"Updated guild: {updated_guild}")

    @discord.ui.channel_select(
        placeholder="Wybierz kanal dla Team2", channel_types=[discord.ChannelType.voice]
    )
    async def configure_team2_channel(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ) -> None:
        """
        Configure guild button callback.

        Args:
        ----
                self (ConfigureGuildView): ConfigureGuildView object.
                button (discord.ui.Button): Button object.
                interaction (discord.Interaction): Interaction object.

        Returns:
        -------
                None

        """
        await interaction.response.defer()
        # TODO add check if interaction.user is owner of guild
        channel = select.values[0]
        await interaction.followup.send(
            f"Kanal dla druzyny Team 2 ustawiony na {channel}", ephemeral=True
        )

        response: Response[Guild] = await guilds_update.asyncio_detailed(
            client=api_client,
            guild_id=self.guild.guild_id,
            body=UpdateGuild(team2_channel=channel.id),
        )
        updated_guild = response.parsed

        logger.logger.debug(f"Updated guild: {updated_guild}")
