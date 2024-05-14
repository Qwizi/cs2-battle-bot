import pytest
from rest_framework import status
from rest_framework.reverse import reverse_lazy

from guilds.models import Guild
from servers.models import Server

API_ENDPOINT = "/api/servers/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_servers_unauthorized_access(methods, api_client, server_data):
    server = Server.objects.create(**server_data)

    if methods == "GET":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response2 = api_client.get(f"{API_ENDPOINT}{server.id}/")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "POST":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "PUT":
        response = api_client.put(f"{API_ENDPOINT}{server.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "PATCH":
        response = api_client.patch(f"{API_ENDPOINT}{server.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "DELETE":
        response = api_client.delete(f"{API_ENDPOINT}{server.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_empty_servers_list(client_with_api_key):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_servers_list(client_with_api_key, server):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == server.id
    assert response.data["results"][0]["ip"] == server.ip
    assert response.data["results"][0]["name"] == server.name
    assert response.data["results"][0]["port"] == server.port
    assert response.data["results"][0]["password"] == server.password
    assert response.data["results"][0]["is_public"] == server.is_public

    # Ensure that the rcon_password is not exposed
    assert "rcon_password" not in response.data["results"][0]


@pytest.mark.django_db
def test_get_server_detail(client_with_api_key, server):
    response = client_with_api_key.get(f"{API_ENDPOINT}{server.id}/")
    assert response.status_code == 200
    assert response.data["id"] == server.id
    assert response.data["ip"] == server.ip
    assert response.data["name"] == server.name
    assert response.data["port"] == server.port
    assert response.data["password"] == server.password
    assert response.data["is_public"] == server.is_public
    assert response.data["join_url"] == reverse_lazy(
        "server-join", args=[server.id], request=response.wsgi_request
    )

    # Ensure that the rcon_password is not exposed
    assert "rcon_password" not in response.data


@pytest.mark.django_db
def test_create_public_server(client_with_api_key, server_data):
    response = client_with_api_key.post(API_ENDPOINT, server_data)
    assert response.status_code == 201
    assert response.data["ip"] == server_data["ip"]
    assert response.data["name"] == server_data["name"]
    assert response.data["port"] == server_data["port"]
    assert response.data["password"] == server_data["password"]
    assert response.data["is_public"] == server_data["is_public"]

    # Ensure that the rcon_password is not exposed
    assert "rcon_password" not in response.data

    # Check if guild is None
    assert response.data["guild"] is None


@pytest.mark.django_db
def test_create_public_server_with_rcon_password(client_with_api_key, server_data):
    server_data["rcon_password"] = "changeme"
    response = client_with_api_key.post(API_ENDPOINT, server_data)
    assert response.status_code == 201
    assert response.data["ip"] == server_data["ip"]
    assert response.data["name"] == server_data["name"]
    assert response.data["port"] == server_data["port"]
    assert response.data["password"] == server_data["password"]
    assert response.data["is_public"] == server_data["is_public"]

    # Ensure that the rcon_password is not exposed
    assert "rcon_password" not in response.data

    # check that the rcon_password is saved
    server = Server.objects.get(id=response.data["id"])
    assert server.rcon_password == server_data["rcon_password"]

    # Check if guild is None
    assert response.data["guild"] is None


@pytest.mark.django_db
def test_create_server_with_guild(client_with_api_key, server_data, guild_data):
    guild = Guild.objects.create_guild(**guild_data)
    server_data["guild"] = guild.id
    response = client_with_api_key.post(API_ENDPOINT, server_data)
    assert response.status_code == 201
    assert response.data["guild"] == guild.id


@pytest.mark.django_db
def test_get_servers_list_with_guild_filter(
    client_with_api_key, server_data, guild_data
):
    server = Server.objects.create(**server_data)
    guild = Guild.objects.create_guild(**guild_data)
    server2 = Server.objects.create(
        ip="127.0.0.1",
        port=27016,
        name="Guild Server",
        password="changeme",
        rcon_password="test",
        is_public=False,
        guild=guild,
    )
    server3 = Server.objects.create(
        ip="127.0.0.1",
        port=27016,
        name="Guild Server",
        password="changeme",
        rcon_password="test",
        is_public=False,
    )
    response = client_with_api_key.get(f"{API_ENDPOINT}?guild_or_public={guild.id}")
    assert response.status_code == 200
    assert response.data["count"] == 2
    assert Server.objects.count() == 3

    # Ensure that the rcon_password is not exposed
    assert "rcon_password" not in response.data["results"][0]


@pytest.mark.django_db
def test_delete_server(client_with_api_key, server):
    response = client_with_api_key.delete(f"{API_ENDPOINT}{server.id}/")
    assert response.status_code == 204
    assert Server.objects.count() == 0
    assert not Server.objects.filter(id=server.id).exists()


@pytest.mark.django_db
def test_server_join(client_with_api_key, server):
    response = client_with_api_key.get(f"{API_ENDPOINT}{server.id}/join/")
    assert response.status_code == 301
    assert (
        response.url == f"steam://connect/{server.ip}:{server.port}/{server.password}"
    )
