import pytest
from steam import game_servers as gs
from servers.models import Server


@pytest.mark.django_db
def test_create_server(server_data):
    server = Server.objects.create(**server_data)
    assert server.ip == server_data["ip"]
    assert server.name == server_data["name"]
    assert server.port == server_data["port"]
    assert server.password == server_data["password"]
    assert server.rcon_password == server_data["rcon_password"]
    assert server.is_public == server_data["is_public"]


@pytest.mark.django_db
def test_get_connect_string(server_data):
    server = Server.objects.create(**server_data)
    connect_string = server.get_connect_string()
    assert (
        connect_string
        == f"connect {server.ip}:{server.port}; password {server.password};"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("valid", [True, False])
def test_check_online_server(valid, server_data):
    if valid:
        cs2_server_query = r"\appid\730\empty\1\secure\1"
        server_addr = next(gs.query_master(cs2_server_query))  # single CS2 Server
        server = Server.objects.create(
            ip=server_addr[0], port=server_addr[1], name="Test server"
        )
        assert server.check_online() is True
    else:
        server = Server.objects.create(**server_data)
        assert server.check_online() is False


@pytest.mark.django_db
def test_get_join_link(server_data):
    server = Server.objects.create(**server_data)
    join_link = server.get_join_link()
    assert join_link == f"steam://connect/{server.ip}:{server.port}/{server.password}"
