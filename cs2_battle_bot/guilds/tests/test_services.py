import pytest
from django.contrib.auth import get_user_model

from guilds.models import Guild
from guilds.services import create_guild_if_not_exists
from accounts.tests.conftest import user as user_fixture
User = get_user_model()
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_guild_if_not_exits_guild_not_exists(user_fixture):
    guild_id = "123456"
    guild_name = "test_guild"
    # Fetch the user and guild from the database
    await create_guild_if_not_exists(
        user_fixture[0].username,  # Assuming user_fixture is a User instance
        guild_id,
        guild_name
    )
    guild = await Guild.objects.aget(guild_id=guild_id)

    # Assertions to verify the guild and user have been created/fetched correctly
    assert guild.name == guild_name
    assert guild.guild_id == guild_id
    assert guild.owner.username == user_fixture[0].username
