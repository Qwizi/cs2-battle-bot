import pytest

from players.models import Team


@pytest.mark.django_db
def test_teams_model(players):
    team = Team.objects.create(name="Team 1")
    players_in_team = players[:5]
    team.players.set(players_in_team)
    team.leader = players_in_team[0]
    team.save()
    assert team.name == "Team 1"
    assert team.players.count() == 5
    assert team.leader == players[0]

    players_dict = team.get_players_dict()

    assert len(players_dict) == 5

    # Check if the players_dict is a list of dictionaries
    # like {"76561199105283370": "♣ kashana"}
    assert isinstance(players_dict, dict)
    for steamid64, username in players_dict.items():
        assert steamid64 in [player.steam_user.steamid64 for player in players_in_team]
        assert username in [player.steam_user.username for player in players_in_team]
