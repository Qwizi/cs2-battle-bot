import pytest

from guilds.factories import GuildFactory
from accounts.tests.conftest import user as user_fixture


@pytest.mark.django_db
@pytest.fixture
def guild(user_fixture):
    return GuildFactory(owner=user_fixture[0])
