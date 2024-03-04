from random import shuffle
from dotenv import load_dotenv
import httpx
import os
import discord

load_dotenv()

API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")
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


async def create_match(data):
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            MATCHES_ENDPOINT,
            json=data,
        )
        response.raise_for_status()
        data = None
        if response.status_code == 201:
            data = response.json()
        return data, response


async def get_curent_match():
    print(API_URL, headers, CURRENT_MATCH_ENDPOINT)
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(CURRENT_MATCH_ENDPOINT)
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def get_match(match_id: int):
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.get(f"{MATCHES_ENDPOINT}{match_id}/")
        response.raise_for_status()
        data = None
        if response.status_code == 200:
            data = response.json()
        return data, response


async def load_match():
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(LOAD_MATCH_ENDPOINT)
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


async def ban_map(match_id: str, team_id: str, map_tag: str):
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/map_ban/",
            json={
                "team_id": team_id,
                "map_tag": map_tag,
            },
        )
        response.raise_for_status()
        data = None
        if response.status_code == 201:
            data = response.json()
        return data, response


async def pick_map(match_id: str, team_id: str, map_tag: str):
    async with httpx.AsyncClient(base_url=API_URL, headers=headers) as client:
        response = await client.post(
            f"{MATCHES_ENDPOINT}{match_id}/map_pick/",
            json={
                "team_id": team_id,
                "map_tag": map_tag,
            },
        )
        response.raise_for_status()
        data = None
        if response.status_code == 201:
            data = response.json()
        return data, response
