import pytest
from rest_framework import status

from players.models import SteamUser


API_ENDPOINT = "/api/steam-users/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "patch", "delete"])
def test_steam_user_unauthorized(methods, api_client, steam_user_data):
    steam_user = SteamUser.objects.create(**steam_user_data)

    if methods == "get":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response2 = api_client.get(f"{API_ENDPOINT}{steam_user.id}/")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_ENDPOINT}{steam_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "patch":
        response = api_client.patch(f"{API_ENDPOINT}{steam_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_ENDPOINT}{steam_user.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_steam_users_empty_list(client_with_api_key):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_steam_users_list(client_with_api_key, steam_user_data):
    steam_user = SteamUser.objects.create(**steam_user_data)
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["username"] == steam_user_data["username"]
    assert response.data["results"][0]["steamid64"] == steam_user_data["steamid64"]
    assert response.data["results"][0]["steamid32"] == steam_user_data["steamid32"]
    assert response.data["results"][0]["profile_url"] == steam_user_data["profile_url"]
    assert response.data["results"][0]["avatar"] == steam_user_data["avatar"]
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_steam_user(client_with_api_key, steam_user_data):
    steam_user = SteamUser.objects.create(**steam_user_data)
    response = client_with_api_key.get(f"{API_ENDPOINT}{steam_user.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == steam_user_data["username"]
    assert response.data["steamid64"] == steam_user_data["steamid64"]
    assert response.data["steamid32"] == steam_user_data["steamid32"]
    assert response.data["profile_url"] == steam_user_data["profile_url"]
    assert response.data["avatar"] == steam_user_data["avatar"]


@pytest.mark.django_db
def test_create_steam_user(client_with_api_key, steam_user_data):
    response = client_with_api_key.post(API_ENDPOINT, steam_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == steam_user_data["username"]
    assert response.data["steamid64"] == steam_user_data["steamid64"]
    assert response.data["steamid32"] == steam_user_data["steamid32"]
    assert response.data["profile_url"] == steam_user_data["profile_url"]
    assert response.data["avatar"] == steam_user_data["avatar"]


@pytest.mark.django_db
def test_delete_steam_user(client_with_api_key, steam_user_data):
    steam_user = SteamUser.objects.create(**steam_user_data)
    response = client_with_api_key.delete(f"{API_ENDPOINT}{steam_user.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert SteamUser.objects.count() == 0
