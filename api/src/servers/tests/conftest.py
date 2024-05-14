import pytest

from servers.models import Server


@pytest.fixture
def server_data():
    return {
        "ip": "127.0.0.1",
        "name": "Test Server",
        "port": 27015,
        "password": "changeme",
        "rcon_password": "changeme",
        "is_public": True,
    }


@pytest.fixture
def server(server_data):
    return Server.objects.create(**server_data)
