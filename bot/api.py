from __future__ import annotations

import discord
import httpx

from bot.schemas import (
    CreateBanMap,
    CreateMatch,
    CreatePickMap,
    CurrentMatch,
    MapManMany,
    Match,
)
from bot.settings import settings

API_URL = settings.API_URL
API_TOKEN = settings.API_TOKEN
MATCHES_ENDPOINT = "/api/matches/"
CURRENT_MATCH_ENDPOINT = MATCHES_ENDPOINT + "current/"
PLAYERS_ENDPOINT = "/api/players/"
TEAMS_ENDPOINT = "/api/teams/"
LOAD_MATCH_ENDPOINT = "/api/matches/load/"

headers = {
    "X-Api-Key": f"{API_TOKEN}",
}


def get_connect_account_link():
    return f"{API_URL}/accounts/discord/"


async def create_match(data: CreateMatch) -> tuple[Match, httpx.Response]:
    """
    Create a match.

    Args:
    ----
        data (CreateMatch): The match data.

    Returns:
    -------
        tuple[Match, httpx.Response]: The match and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            MATCHES_ENDPOINT,
            json=data.model_dump(),
        )
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.CREATED:
            data = response.json()
            data = Match(**data)
        return data, response


async def get_curent_match() -> tuple[CurrentMatch, httpx.Response]:
    """
    Get the current match.

    Args:
    ----
        None

    Returns:
    -------
        tuple[CurrentMatch, httpx.Response]: The current match and the response.

    """
    print(API_URL, headers, CURRENT_MATCH_ENDPOINT)
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(CURRENT_MATCH_ENDPOINT)
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.OK:
            data = response.json()
            data = CurrentMatch(**data)
        return data, response


async def get_match(match_id: int) -> tuple[Match, httpx.Response]:
    """
    Get a match.

    Args:
    ----
        match_id (int): The match id.

    Returns:
    -------
        tuple[Match, httpx.Response]: The match and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(f"{MATCHES_ENDPOINT}{match_id}/")
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.OK:
            data = response.json()
            data = Match(**data)
        return data, response


async def load_match():
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(LOAD_MATCH_ENDPOINT, timeout=15)
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def get_players():
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(PLAYERS_ENDPOINT)
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def get_player(player_id: str):
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(PLAYERS_ENDPOINT + player_id)
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def get_teams():
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(TEAMS_ENDPOINT)
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def get_teams_autocomplete(ctx: discord.AutocompleteContext):
    try:
        if "shuffle_teams" in ctx.options:
            shuffle_teams = ctx.options["shuffle_teams"]
            if shuffle_teams:
                return ["Team 1", "Team 2"]
        teams_data, response = await get_teams()
        teams = teams_data.get("results")
        return [team["name"] for team in teams]
    except httpx.HTTPError as e:
        print(e)
        return []


async def ban_map(data: CreateBanMap) -> tuple[Match, httpx.Response]:
    """
    Ban a map.

    Args:
    ----
        data (BanMap): The map ban data.

    Returns:
    -------
        tuple[Match, httpx.Response]: The match and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        data = data.model_dump()
        match_id = data.pop("match_id")
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/map_ban/", json=data
        )
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.CREATED:
            data = response.json()
            data = Match(**data)
        return data, response


async def get_match_map_bans(match_id: str) -> tuple[MapManMany, httpx.Response]:
    """

    Get match map bans.

    Args:
    ----
        match_id (str): The match id.

    Returns:
    -------
        tuple[MapManMany, httpx.Response]: The map bans and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(
            f"{MATCHES_ENDPOINT}{match_id}/bans/",
        )
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.OK:
            data = response.json()
            data = MapManMany(**data)
        return data, response


async def get_match_map_picks(match_id: str) -> tuple[MapManMany, httpx.Response]:
    """

    Get match map picks.

    Args:
    ----
        match_id (str): The match id.

    Returns:
    -------
        tuple[MapManMany, httpx.Response]: The map picks and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(
            f"{MATCHES_ENDPOINT}{match_id}/picks/",
        )
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.OK:
            data = response.json()
            data = MapManMany(**data)
        return data, response


async def pick_map(data: CreatePickMap) -> tuple[Match, httpx.Response]:
    """
    Pick a map.

    Args:
    ----
        data (PickMap): The map pick data.

    Returns:
    -------
        tuple[Match, httpx.Response]: The match and the response.

    """
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        data = data.model_dump()
        match_id = data.pop("match_id")
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/map_pick/",
            json=data,
        )
        response.raise_for_status()
        data = None
        if response.status_code == httpx.codes.CREATED:
            data = response.json()
            data = Match(**data)
        return data, response


async def recreate_match(match_id: str) -> tuple[Match, httpx.Response]:
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/recreate/",
        )
        response.raise_for_status()
        data = None
        if response.status_code == 201:
            data = response.json()
            data = Match(**data)
        return data, response


async def shuffle_teams(match_id: str) -> tuple[Match, httpx.Response]:
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/shuffle_teams/",
        )
        response.raise_for_status()
        data = None
        if response.status_code == 201:
            data = response.json()
            data = Match(**data)

        return data, response
