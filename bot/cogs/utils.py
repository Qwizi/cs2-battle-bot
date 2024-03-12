"""Utility functions for the bot."""

from __future__ import annotations

import discord

from bot.schemas import Match


def get_discord_users_ids(players: list[dict]) -> list[int]:
    """
    Return list of discord users ids from players list.

    Args:
    ----
        players (list[dict]): List of players.

    Returns:
    -------
        list[int]: List of discord users ids.

    """
    user_ids = []
    try:
        for player in players:
            discord_user = player["discord_user"]
            user_id = discord_user["user_id"]
            user_ids.append(int(user_id))
    except (KeyError, TypeError):
        pass
    return user_ids


def get_teams_discord_users_ids(
    team1: dict[str], team2: dict[str]
) -> tuple[list[int], list[int]]:
    """
    Get discord users ids from teams.

    Args:
    ----
        team1 (dict[str]): Team 1.
        team2 (dict[str]): Team 2.

    Returns:
    -------
        tuple[list[int], list[int]]: Tuple of lists of discord users ids.

    """
    if not team1 or not team2:
        return [], []
    team1_players = team1.get("players")
    team2_players = team2.get("players")
    if not team1_players or not team2_players:
        return [], []
    team1_discord_users_ids = get_discord_users_ids(team1.get("players"))
    team2_discord_users_ids = get_discord_users_ids(team2.get("players"))
    return team1_discord_users_ids, team2_discord_users_ids


def check_user_is_in_team(user_id: int, team1: dict[str], team2: dict[str]) -> bool:
    """
    Check if user is in team.

    Args:
    ----
        user_id (int): User id.
        team1 (dict[str]): Team 1.
        team2 (dict[str]): Team 2.

    Returns:
    -------
        bool: True if user is in team, False otherwise.

    """
    (
        team1_discord_users_ids,
        team2_discord_users_ids,
    ) = get_teams_discord_users_ids(team1, team2)
    if (
        user_id not in team1_discord_users_ids
        and user_id not in team2_discord_users_ids
    ):
        return False
    return True


def get_team_leader_discord_user_id(team: dict[str]) -> None | int:
    """
    Get team leader discord user id.

    Args:
    ----
        team (dict[str]): Team.

    Returns:
    -------
        int: Team leader discord user id.

    """
    try:
        return int(team["players"][0]["discord_user"]["user_id"])
    except ValueError:
        return None


def get_team_leader_discord_username(team: dict[str]) -> None | str:
    """
    Get team Leader name.

    Args:
    ----
        team (dict[str]): Team.

    Returns:
    -------
        str: Team leader name.

    """
    try:
        return team["players"][0]["discord_user"]["username"]
    except ValueError:
        return None


def get_team_leaders_discord_id(
    team1: dict[str], team2: dict[str]
) -> tuple[int, int] | tuple[None, None]:
    """
    Get team leaders discord ids.

    Args:
    ----
        team1 (dict[str]): Team 1.
        team2 (dict[str]): Team 2.

    Returns:
    -------
        tuple[int, int]: Tuple of team leaders discord ids.

    """
    team1_leader = get_team_leader_discord_user_id(team1)
    team2_leader = get_team_leader_discord_user_id(team2)
    if not team1_leader or not team2_leader:
        return None, None
    return team1_leader, team2_leader


def check_is_user_leader(user_id: int, team1: dict[str], team2: dict[str]) -> bool:
    """
    Check if user is leader of team.

    Args:
    ----
        user_id (int): User id.
        team1 (dict[str]): Team 1.
        team2 (dict[str]): Team 2.

    Returns:
    -------
        bool: True if user is leader of team, False otherwise.

    """
    team1_leader, team2_leader = get_team_leaders_discord_id(team1, team2)
    if user_id not in {team1_leader, team2_leader}:
        return False
    return True


def check_is_user_can_pick(user_id: int, map_picks: list[dict], testing: bool) -> bool:  # noqa: FBT001
    """
    Check if user can pick map.

    Args:
    ----
        user_id (int): User id.
        map_picks (list[dict]): List of map picks.
        testing (bool): Testing mode.


    Returns:
    -------
        bool: True if user can pick map, False otherwise.

    """
    if len(map_picks) == 0:
        return True
    last_map_pick = map_picks[-1]
    last_pick_team = last_map_pick.get("team")
    last_pick_team_leader = get_team_leader_discord_user_id(last_pick_team)
    if not testing and user_id == last_pick_team_leader:
        return False
    return True


def mention_user(user_id: int) -> str:
    """
    Mention user.

    Args:
    ----
        user_id (int): User id.

    Returns:
    -------
        str: Mentioned user.

    """
    return f"<@{user_id}>"


def get_mentioned_users(players: list[dict]) -> list[str]:
    """
    Get mentioned users.

    Args:
    ----
        players (list[dict]): List of players.

    Returns:
    -------
        list[str]: List of mentioned users.

    """
    if not players:
        return []
    mentioned_users = []
    try:
        for player in players:
            mentioned_user = mention_user(int(player["discord_user"]["user_id"]))
            mentioned_users.append(mentioned_user)
    except (KeyError, TypeError):
        pass
    return mentioned_users


def get_last_team_pick(map_picks: list[dict]) -> None:
    """
    Get last team pick.

    Args:
    ----
        map_picks (list[dict]): List of map picks.

    Returns:
    -------
        dict[str]: Last team pick.

    """
    if len(map_picks) == 0:
        return None
    return map_picks[-1].get("team")


def get_last_team_ban(map_bans: list[dict]) -> None:
    """
    Get last team ban.

    Args:
    ----
        map_bans (list[dict]): List of map bans.

    Returns:
    -------
        dict[str]: Last team ban.

    """
    if len(map_bans) == 0:
        return None
    return map_bans[-1].get("team")


def create_match_embed(match: Match, author_id: int) -> discord.Embed:
    """
    Create match embed.

    Args:
    ----
        match (dict): Match.
        author_id (int): Author id.

    Returns:
    -------
        discord.Embed: Match embed.

    """
    teams = [match.team1, match.team2]
    embed = discord.Embed(
        title="Mecz utworzony!",
        description="Mecz został utworzony.",
        color=discord.Colour.blurple(),
    )
    for team in teams:
        team_name = team.get("name")
        team_players = team.get("players")
        team_names = get_mentioned_users(team_players)
        leader_id = get_team_leader_discord_user_id(team)
        leader = mention_user(leader_id)
        embed.add_field(name=team_name, value=f"{', '.join(team_names)}", inline=False)
        embed.add_field(name="Lider", value=leader, inline=False)

    embed.set_footer(text=author_id)
    return embed


def update_match_embed_with_maps(
    old_embed: discord.Embed, maps: list[str], author_id: int
) -> discord.Embed:
    """
    Creates a new embed from an existing one, adding a "Map" field with provided maps.

    Args:
    ----
        old_embed (discord.Embed): The existing embed to update.
        maps (list[str]): A list of map names.
        author_id (int): The author's Discord ID for the footer.

    Returns:
    -------
        discord.Embed: The new embed with the updated "Map" field.

    """
    new_embed = discord.Embed.from_dict(
        old_embed.to_dict()
    )  # Efficiently copy embed data
    maps_text = ", ".join(maps)

    # Check for existing "Map" field using list comprehension
    existing_map_field = [field for field in new_embed.fields if field.name == "Map"]

    if existing_map_field:
        # Update existing "Map" field at its index (likely 0)
        new_embed.set_field_at(
            existing_map_field[0].index, name="Map", value=maps_text, inline=False
        )
    else:
        # Add new "Map" field
        new_embed.add_field(name="Map", value=maps_text, inline=False)

    new_embed.set_footer(text=author_id)
    return new_embed
