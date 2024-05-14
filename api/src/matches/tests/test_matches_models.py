import pytest
from django.test import RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse_lazy

from matches.models import Match, MatchStatus, MatchType, MatchConfig, GameMode
from cs2_battle_bot.tests.conftest import configs, bo1_configs


@pytest.mark.django_db
@pytest.mark.parametrize("with_server", [True, False])
@pytest.mark.parametrize("config", configs)
def test_match_model(with_server, server, config, guild, default_author):
    server = server if with_server else None
    factory = RequestFactory()

    # Create a request
    request = factory.get("/")
    match_config = MatchConfig.objects.get(name=config)
    new_match: Match = Match.objects.create(
        config=match_config,
        author=default_author.player.discord_user,
        guild=guild,
        server=server,
    )
    new_match.create_webhook_cvars(
        str(reverse_lazy("match-webhook", args=[new_match.pk], request=request))
    )
    assert new_match.status == MatchStatus.CREATED

    assert new_match.config.name == match_config.name
    assert new_match.config.game_mode == match_config.game_mode
    assert new_match.config.type == match_config.type
    assert new_match.config.clinch_series == match_config.clinch_series
    assert new_match.config.max_players == match_config.max_players
    assert new_match.config.map_pool == match_config.map_pool
    assert new_match.config.map_sides == match_config.map_sides

    assert new_match.team1 is not None
    assert new_match.team2 is not None
    assert new_match.team1.name == "Team 1"
    assert new_match.team2.name == "Team 2"
    assert new_match.winner_team is None
    assert new_match.map_bans.count() == 0
    assert new_match.map_picks.count() == 0
    assert new_match.last_map_ban is None
    assert new_match.last_map_pick is None
    assert new_match.maplist is None
    assert new_match.server == server
    assert new_match.guild == guild
    assert new_match.author == default_author.player.discord_user
    assert new_match.message_id is None
    assert new_match.embed is not None

    team1_players_dict = new_match.get_team1_players_dict()
    team2_players_dict = new_match.get_team2_players_dict()

    assert team1_players_dict["name"] == "Team 1"
    assert team2_players_dict["name"] == "Team 2"

    assert len(team1_players_dict["players"]) == 1
    assert len(team2_players_dict["players"]) == 0

    assert new_match.api_key_header == "Authorization"
    assert new_match.load_match_command_name == "matchzy_loadmatch_url"
    assert new_match.get_author_token() == Token.objects.get(user=default_author).key
    assert (
        new_match.get_connect_command() == ""
        if with_server is False
        else server.get_connect_string()
    )

    matchzy_config = new_match.get_matchzy_config()
    assert matchzy_config["matchid"] == new_match.pk
    assert matchzy_config["team1"] == team1_players_dict
    assert matchzy_config["team2"] == team2_players_dict
    assert matchzy_config["num_maps"] == 1 if match_config.type == MatchType.BO1 else 3
    assert matchzy_config["maplist"] == new_match.maplist
    assert matchzy_config["map_sides"] == match_config.map_sides
    assert matchzy_config["clinch_series"] == match_config.clinch_series
    assert matchzy_config["players_per_team"] == 1
    assert matchzy_config["cvars"] == new_match.cvars
    assert matchzy_config["cvars"]["matchzy_remote_log_url"] == reverse_lazy(
        "match-webhook", args=[new_match.pk], request=request
    )
    assert (
        matchzy_config["cvars"]["matchzy_remote_log_header_key"]
        == new_match.api_key_header
    )
    assert (
        matchzy_config["cvars"]["matchzy_remote_log_header_value"]
        == f"Bearer {new_match.get_author_token()}"
    )

    if match_config.game_mode == GameMode.WINGMAN:
        assert matchzy_config["wingman"] is True

    assert new_match.api_key_header == "Authorization"
    assert new_match.load_match_command_name == "matchzy_loadmatch_url"


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_get_team1_players_dict(match, config):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    team1_dict = match.get_team1_players_dict()
    assert team1_dict["name"] == match.team1.name
    assert len(team1_dict["players"]) == match.team1.players.count()
    assert len(team1_dict["players"]) == 1


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_get_team2_players_dict(match, config):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    team2_dict = match.get_team2_players_dict()
    assert team2_dict["name"] == match.team2.name
    assert len(team2_dict["players"]) == match.team2.players.count()
    assert len(team2_dict["players"]) == 0


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_get_matchzy_config(rf, match, config):
    request = rf.get("/")
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    matchzy_config = match.get_matchzy_config()
    assert matchzy_config["matchid"] == match.pk
    assert matchzy_config["team1"] == match.get_team1_players_dict()
    assert matchzy_config["team2"] == match.get_team2_players_dict()
    assert matchzy_config["num_maps"] == 1 if match.config.type == MatchType.BO1 else 3
    assert matchzy_config["maplist"] == match.maplist
    assert matchzy_config["map_sides"] == match.config.map_sides
    assert matchzy_config["clinch_series"] == match.config.clinch_series
    assert matchzy_config["players_per_team"] == 1
    assert matchzy_config["cvars"] == match.cvars
    assert matchzy_config["cvars"]["matchzy_remote_log_url"] == reverse_lazy(
        "match-webhook", args=[match.pk], request=request
    )
    assert (
        matchzy_config["cvars"]["matchzy_remote_log_header_key"] == match.api_key_header
    )
    assert (
        matchzy_config["cvars"]["matchzy_remote_log_header_value"]
        == f"Bearer {match.get_author_token()}"
    )

    if match.config.game_mode == GameMode.WINGMAN:
        assert matchzy_config["wingman"] is True


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_get_connect_command(match, server, config):
    match.server = server
    match.save()
    assert match.get_connect_command() == server.get_connect_string()


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_get_author_token(match, default_author, config):
    match.config = MatchConfig.objects.get(name=config)
    assert match.get_author_token() == Token.objects.get(user=default_author).key


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_create_webhook_cvars(rf, match, config):
    request = rf.get("/")
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    match.create_webhook_cvars(
        str(reverse_lazy("match-webhook", args=[match.pk], request=request))
    )
    assert match.cvars["matchzy_remote_log_url"] == reverse_lazy(
        "match-webhook", args=[match.pk], request=request
    )
    assert match.cvars["matchzy_remote_log_header_key"] == match.api_key_header
    assert (
        match.cvars["matchzy_remote_log_header_value"]
        == f"Bearer {match.get_author_token()}"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_shuffle_players(match, config, players):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    players = players[
        : match.config.max_players - 1
    ]  # -1 because author is already in the match
    for player in players:
        match.add_player_to_match(player)
    team1_players = match.team1.players.all()
    team2_players = match.team2.players.all()

    assert match.team1.players.count() == team1_players.count()
    assert match.team2.players.count() == team2_players.count()
    assert match.team1.leader is None
    assert match.team2.leader is None

    match.shuffle_players()

    assert match.team1.players != team1_players
    assert match.team2.players != team2_players
    assert match.team1.leader is not None
    assert match.team2.leader is not None


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_change_teams_name(match, config, players, default_author):
    player = players[1]
    match.config = MatchConfig.objects.get(name=config)
    match.team1.leader = default_author.player
    match.team2.leader = player
    match.save()

    match.add_player_to_match(player, "team2")

    assert match.team1.name == "Team 1"
    assert match.team2.name == "Team 2"

    match.change_teams_name()

    assert match.team1.name == "team_Qwizi"
    assert match.team2.name == "team_Abdull Mohamed Mother Fakier"


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_add_player_to_match(match, config, players, default_author):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    player = players[1]
    match.add_player_to_match(player)
    assert match.team1.players.count() == 1
    assert match.team2.players.count() == 1
    assert match.author == default_author.player.discord_user
    assert match.team1.leader is None
    assert match.team2.leader is None
    assert player in match.team1.players.all() or player in match.team2.players.all()


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
@pytest.mark.parametrize("team", ["team1", "team2"])
def test_match_add_player_to_team(match, config, players, team):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    player = players[1]
    match.add_player_to_match(player, team)

    team_instance = match.team1 if team == "team1" else match.team2
    assert player in team_instance.players.all()
    assert team_instance.leader is None


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_remove_player_from_match(match, config, players):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    player = players[1]
    match.add_player_to_match(player)
    assert player in match.team1.players.all() or player in match.team2.players.all()
    match.remove_player_from_match(player)
    assert (
        player not in match.team1.players.all()
        and player not in match.team2.players.all()
    )


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_start_match(match, config, players):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    _players = players[
        : match.config.max_players - 1
    ]  # -1 because author is already in the match
    assert match.status == MatchStatus.CREATED
    for player in _players:
        match.add_player_to_match(player)
    match.start_match()

    if match.config.shuffle_teams:
        assert match.team1.leader is not None
        assert match.team2.leader is not None
        assert match.status == MatchStatus.MAP_VETO
    else:
        assert match.status == MatchStatus.CAPTAINS_SELECT


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_match_set_team_capitan(match, config, players):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    _players = players[: match.config.max_players - 1]
    for player in _players:
        match.add_player_to_match(player)
    assert match.team1.leader is None
    assert match.team2.leader is None
    match.set_team_captain(_players[0], "team1")
    match.set_team_captain(_players[1], "team2")

    assert match.team1.leader == _players[0]
    assert match.team2.leader == _players[1]


@pytest.mark.django_db
@pytest.mark.parametrize("config", configs)
def test_get_team_by_player(match, config, players):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    match.add_player_to_match(players[0], "team1")
    match.add_player_to_match(players[1], "team2")
    assert match.get_team_by_player(players[0]) == match.team1
    assert match.get_team_by_player(players[1]) == match.team2


@pytest.mark.django_db
@pytest.mark.parametrize("team", ["team1", "team2"])
@pytest.mark.parametrize("config", bo1_configs)
def test_match_ban_map(match, team, config):
    match.config = MatchConfig.objects.get(name=config)
    match.save()
    _team = getattr(match, team)
    _map = match.config.map_pool.maps.first()
    match.ban_map(_team, map=_map)

    assert match.map_bans.count() == 1
    assert match.last_map_ban.team == _team
    assert match.last_map_ban.map == _map
