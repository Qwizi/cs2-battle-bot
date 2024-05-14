import pytest

from players.models import DiscordUser


@pytest.mark.django_db
def test_discord_user_model(discord_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)
    assert discord_user.user_id == discord_user_data["user_id"]
    assert discord_user.username == discord_user_data["username"]
