import pytest
from rest_framework import status

from players.models import DiscordUser

API_ENDPOINT = "/api/discord-users/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "patch", "delete"])
def test_discord_user_unauthorized(methods, api_client, discord_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)

    if methods == "get":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response2 = api_client.get(f"{API_ENDPOINT}{discord_user.id}/")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_ENDPOINT}{discord_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "patch":
        response = api_client.patch(f"{API_ENDPOINT}{discord_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_ENDPOINT}{discord_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_discord_users_empty_list(client_with_api_key):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_discord_users_list(client_with_api_key, discord_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["user_id"] == discord_user_data["user_id"]
    assert response.data["results"][0]["username"] == discord_user_data["username"]
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_discord_user(client_with_api_key, discord_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)
    response = client_with_api_key.get(f"{API_ENDPOINT}{discord_user.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["user_id"] == discord_user_data["user_id"]
    assert response.data["username"] == discord_user_data["username"]


@pytest.mark.django_db
def test_create_discord_user(client_with_api_key, discord_user_data):
    response = client_with_api_key.post(API_ENDPOINT, discord_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user_id"] == discord_user_data["user_id"]
    assert response.data["username"] == discord_user_data["username"]


@pytest.mark.django_db
def test_delete_discord_user(client_with_api_key, discord_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)
    response = client_with_api_key.delete(f"{API_ENDPOINT}{discord_user.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert DiscordUser.objects.count() == 0
