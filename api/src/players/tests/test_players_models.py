import pytest


@pytest.mark.django_db
def test_player_model(player):
    assert player.discord_user
    assert player.steam_user
