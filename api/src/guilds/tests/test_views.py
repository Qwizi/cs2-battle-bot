import pytest
from rest_framework import status
from guilds.models import Guild

API_ENDPOINT = "/api/guilds/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "patch", "delete"])
def test_guilds_unauthorized(methods, api_client, guild):
    if methods == "get":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response2 = api_client.get(f"{API_ENDPOINT}{guild.id}/")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_ENDPOINT}{guild.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "patch":
        response = api_client.patch(f"{API_ENDPOINT}{guild.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_ENDPOINT}{guild.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_guilds_empty_list(client_with_api_key):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_guilds_list(client_with_api_key, guild):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == guild.name
    assert response.data["results"][0]["owner"] is not None
    assert response.data["results"][0]["guild_id"] == guild.guild_id
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_guild(client_with_api_key, guild):
    response = client_with_api_key.get(f"{API_ENDPOINT}{guild.guild_id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == guild.name
    assert response.data["owner"] is not None
    assert response.data["guild_id"] == guild.guild_id
    assert response.data["owner"]["username"] == guild.owner.username
    assert response.data["owner"]["player"]["id"] == guild.owner.player.id
    assert (
        response.data["owner"]["player"]["discord_user"]["id"]
        == guild.owner.player.discord_user.id
    )


@pytest.mark.django_db
def test_create_guild(client_with_api_key, guild_data):
    response = client_with_api_key.post(API_ENDPOINT, guild_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == guild_data["name"]
    assert response.data["owner"] is not None
    assert response.data["guild_id"] == guild_data["guild_id"]


@pytest.mark.django_db
def test_delete_guild(client_with_api_key, guild):
    response = client_with_api_key.delete(f"{API_ENDPOINT}{guild.guild_id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Guild.objects.count() == 0


@pytest.mark.django_db
def test_update_guild(client_with_api_key, guild):
    name = "new name"
    lobby_channel = "new_lobby_channel"
    team1_channel = "new_team1_channel"
    team2_channel = "new_team2_channel"
    data = {
        "name": name,
        "lobby_channel": lobby_channel,
        "team1_channel": team1_channel,
        "team2_channel": team2_channel,
    }
    response = client_with_api_key.put(f"{API_ENDPOINT}{guild.guild_id}/", data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == name
    assert response.data["lobby_channel"] == lobby_channel
    assert response.data["team1_channel"] == team1_channel
    assert response.data["team2_channel"] == team2_channel
    assert response.data["owner"] is not None
