import pytest

from players.models import SteamUser


@pytest.mark.django_db
def test_steam_user_model(steam_user_data):
    steam_user = SteamUser.objects.create(**steam_user_data)
    assert steam_user.username == steam_user_data["username"]
    assert steam_user.steamid64 == steam_user_data["steamid64"]
    assert steam_user.steamid32 == steam_user_data["steamid32"]
    assert steam_user.profile_url == steam_user_data["profile_url"]
    assert steam_user.avatar == steam_user_data["avatar"]
    assert SteamUser.objects.count() == 1
