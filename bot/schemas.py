from __future__ import annotations

from typing import Optional

import discord
from pydantic import BaseModel


class CurrentMatchTeam(BaseModel):
    """Schema for the current match team."""

    name: str
    players: dict


class CurrentMatch(BaseModel):
    """Schema for the current match."""

    matchid: int
    team1: CurrentMatchTeam
    team2: CurrentMatchTeam
    num_maps: int
    maplist: list[str]
    map_sides: list[str]
    clinch_series: bool
    players_per_team: int
    cvars: dict


class CreateMatch(BaseModel):
    """Create match serializer."""

    discord_users_ids: list[int]
    team1_id: Optional[str] = None
    team2_id: Optional[str] = None
    shuffle_players: bool = True
    match_type: str
    clinch_series: bool = False
    map_sides: Optional[list[str]] = None
    cvars: dict


class DiscordUser(BaseModel):
    """Discord user serializer."""

    id: str
    user_id: int
    username: str
    created_at: str
    updated_at: str


class SteamUser(BaseModel):
    """Steam user serializer."""

    id: str
    username: str
    steamid64: str
    steamid32: str
    profile_url: str
    avatar: str
    created_at: str
    updated_at: str


class Player(BaseModel):
    """Player serializer."""

    id: str
    discord_user: DiscordUser
    steam_user: SteamUser
    created_at: str
    updated_at: str

    def mention_user(self) -> str:
        """Mention the user."""
        return f"<@{self.discord_user.user_id}>"


class Team(BaseModel):
    """Team serializer."""

    id: str
    name: str
    players: list[Player]
    leader: str
    created_at: str
    updated_at: str


class Map(BaseModel):
    """Map serializer."""

    id: str
    name: str
    tag: str
    created_at: str
    updated_at: str


class MapBan(BaseModel):
    """Map ban serializer."""

    team: Team
    map: Map
    created_at: str
    updated_at: str


class MapManMany(BaseModel):
    """Map ban many serializer."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[MapBan]


class MapPick(BaseModel):
    """Map pick serializer."""

    team: Team
    map: Map
    created_at: str
    updated_at: str


class Match(BaseModel):
    """Match serializer."""

    id: int
    team1: Team
    team2: Team
    type: str
    winner_team: Optional[Team] = None
    maps: list[Map]
    map_bans: list[MapBan]
    map_picks: list[MapPick]
    created_at: str
    updated_at: str

    def check_user_is_in_teams(self, user_id: int) -> bool:
        """Check if user is in team."""
        return user_id in [
            player.discord_user.user_id
            for player in self.team1.players + self.team2.players
        ]

    def check_user_is_leader_in_teams(self, user_id: int) -> bool:
        """Check if user is leader of team."""
        team1_leader, team2_leader = self.get_teams_leaders()
        if user_id not in {
            team1_leader.discord_user.user_id,
            team2_leader.discord_user.user_id,
        }:
            return False
        return True

    def check_user_team_can_ban(self, user_id: int) -> bool:
        """Check if user can ban."""
        user_team = self.get_user_team(user_id)
        team_leader = self.get_team_leader(user_team)
        if user_id != team_leader.discord_user.user_id:
            return False
        try:
            last_map_ban_team = self.map_bans[-1].team
            # if user team is not the same as last map ban team, it means that user team can ban
            if user_team != last_map_ban_team:
                return True
        except IndexError:
            # if there is no map bans, it means that it's first ban and user team must be team1
            if user_team == self.team1:
                return True
        return False

    def get_user_team(self, user_id: int) -> Team | None:
        """Get user team."""
        if user_id in [player.discord_user.user_id for player in self.team1.players]:
            return self.team1
        if user_id in [player.discord_user.user_id for player in self.team2.players]:
            return self.team2
        return None

    def get_team_leader(self, team: str) -> Player:
        """Get team leader."""
        if team == "team1":
            return self.team1.players[0]
        return self.team2.players[0]

    def get_teams_leaders(
        self,
    ) -> list[Player]:
        """Get team leaders discord ids."""
        team1_leader = self.get_team_leader("team1")
        team2_leader = self.get_team_leader("team2")
        return team1_leader, team2_leader

    def get_mentioned_team_leaders(self) -> tuple[str, str] | tuple[None, None]:
        """Get mention team leaders."""
        team1_leader, team2_leader = self.get_teams_leaders()
        return (team1_leader.mention_user(), team2_leader.mention_user())

    def get_mentioned_team_players(self) -> tuple[list[str], list[str]]:
        """Get mentioned team players."""
        team1_mentioned_players = [
            player.mention_user() for player in self.team1.players
        ]
        team2_mentioned_players = [
            player.mention_user() for player in self.team2.players
        ]
        return (team1_mentioned_players, team2_mentioned_players)

    def get_maps_tags(self) -> list[str]:
        """
        Get map tags.

        Args:
        ----
            None

        Returns:
        -------
            list[str]: List of map tags.

        """
        return [map_.tag for map_ in self.maps]

    def create_match_embed(self, author_id: int) -> discord.Embed:
        """
        Create match embed.

        Args:
        ----
            author_id (int): Author id.

        Returns:
        -------
            discord.Embed: Embed with match information.

        """
        (
            team1_mentioned_leader,
            team2_mentioned_leader,
        ) = self.get_mentioned_team_leaders()
        (
            team1_mentioned_players,
            team2_mentioned_players,
        ) = self.get_mentioned_team_players()
        teams = [
            (self.team1.name, team1_mentioned_leader, team1_mentioned_players),
            (self.team2.name, team2_mentioned_leader, team2_mentioned_players),
        ]
        embed = discord.Embed(
            title="Mecz utworzony!",
            description="Mecz został utworzony.",
            color=discord.Colour.blurple(),
        )

        for team in teams:
            team_name, team_leader, team_players = team
            embed.add_field(
                name=team_name,
                value=", ".join(team_players),
                inline=False,
            )
            embed.add_field(
                name="Leader",
                value=team_leader,
                inline=False,
            )
        embed.set_footer(text=author_id)
        return embed


class CreateBanMap(BaseModel):
    """Ban map serializer."""

    match_id: int
    team_id: str
    map_tag: str


class CreatePickMap(CreateBanMap):
    """Pick map serializer."""
