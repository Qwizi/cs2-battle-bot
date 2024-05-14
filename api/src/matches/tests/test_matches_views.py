import pytest
from rest_framework import status

from matches.models import Match, MatchType, MatchStatus
from servers.models import Server

API_ENDPOINT = "/api/matches/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "delete"])
@pytest.mark.parametrize(
    "actions",
    ["load", "webhook", "ban", "pick", "recreate", "shuffle", "config", "join"],
)
def test_match_unauthorized(api_client, client_with_api_key, methods, actions, match):
    if methods == "get":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        if actions == "config":
            response = api_client.get(f"{API_ENDPOINT}{match.pk}/config/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            response = client_with_api_key.get(f"{API_ENDPOINT}{match.pk}/config/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        if actions == "load":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/load/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "webhook":
            response = api_client.post(f"{API_ENDPOINT}webhook/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "ban":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/ban/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "pick":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/pick/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "recreate":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/recreate/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "shuffle":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/shuffle/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        elif actions == "join":
            response = api_client.post(f"{API_ENDPOINT}{match.pk}/join/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_ENDPOINT}{match.pk}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_ENDPOINT}{match.pk}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_matches_list(client_with_api_key, match, match_with_server):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == Match.objects.count()
    assert response.data["results"][0]["id"] == match.pk
    assert response.data["results"][0]["status"] == match.status
    assert response.data["results"][0]["type"] == match.type
    assert response.data["results"][0]["author"]["id"] == match.author.pk
    assert response.data["results"][0]["team1"]["id"] == match.team1.pk
    assert response.data["results"][0]["team2"]["name"] == match.team2.name
    assert response.data["results"][0]["team2"]["id"] == match.team2.pk
    assert response.data["results"][0]["team2"]["name"] == match.team2.name
    assert response.data["results"][0]["players_per_team"] == match.players_per_team
    assert response.data["results"][0]["clinch_series"] == match.clinch_series
    assert response.data["results"][0]["map_sides"] == match.map_sides
    assert response.data["results"][0]["created_at"] is not None
    assert response.data["results"][0]["updated_at"] is not None

    assert response.data["results"][1]["id"] == match_with_server.pk
    assert response.data["results"][1]["server"]["id"] == match_with_server.server.pk
    assert "rcon_password" not in response.data["results"][1]["server"]
    assert response.data["next"] is None
    assert response.data["previous"] is None

    assert response.data["results"][0]["guild"]["id"] == match.guild.pk


@pytest.mark.django_db
@pytest.mark.parametrize("with_server", [True, False])
def test_get_match(client_with_api_key, match, match_with_server, with_server):
    match_to_test = match if not with_server else match_with_server
    response = client_with_api_key.get(f"{API_ENDPOINT}{match_to_test.pk}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == match_to_test.pk
    assert response.data["status"] == match_to_test.status
    assert response.data["type"] == match_to_test.type
    assert response.data["author"]["id"] == match_to_test.author.pk
    assert response.data["team1"]["id"] == match_to_test.team1.pk
    assert response.data["team2"]["name"] == match_to_test.team2.name
    assert response.data["team2"]["id"] == match_to_test.team2.pk
    assert response.data["players_per_team"] == match_to_test.players_per_team
    assert response.data["clinch_series"] == match_to_test.clinch_series
    assert response.data["map_sides"] == match_to_test.map_sides
    assert response.data["cvars"] is not None
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None
    assert response.data["connect_command"] == (
        "" if not with_server else match_with_server.server.get_connect_string()
    )
    assert response.data["load_match_command"] is not None
    assert response.data["map_bans"] == []
    assert response.data["map_picks"] == []
    if with_server:
        assert response.data["server"]["id"] == match_with_server.server.pk
        assert "rcon_password" not in response.data["server"]

    assert response.data["maplist"] == match_to_test.maplist
    assert response.data["maps"] != []
    assert response.data["guild"]["id"] == match.guild.pk


@pytest.mark.django_db
@pytest.mark.parametrize("with_server", [True, False])
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
@pytest.mark.parametrize("clinch_series", [True, False])
@pytest.mark.parametrize(
    "map_sides", [["knife", "knife", "knife"], ["knife", "team2_ct", "team1_t"]]
)
@pytest.mark.parametrize("cvars", [{"sv_cheats": "1"}])
def test_create_match(
    client_with_api_key,
    match_data,
    with_server,
    match_type,
    server,
    mocker,
    map_sides,
    clinch_series,
    cvars,
):
    match_data["match_type"] = match_type
    if with_server:
        match_data["server_id"] = server.pk
    match_data["clinch_series"] = clinch_series
    match_data["map_sides"] = map_sides
    match_data["cvars"] = cvars
    mocker.patch.object(Server, "check_online", return_value=True)
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == MatchStatus.CREATED
    assert response.data["type"] == match_type
    assert response.data["clinch_series"] == clinch_series
    assert response.data["map_sides"] == map_sides
    assert response.data["players_per_team"] == 5
    assert response.data["cvars"]["sv_cheats"] == "1"


@pytest.mark.django_db
def test_create_match_with_maplist(client_with_api_key, match_data):
    match_data["match_type"] = MatchType.BO3
    match_data["maplist"] = ["de_mirage", "de_nuke", "de_inferno"]
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["maplist"] == match_data["maplist"]
    assert response.data["config"]["maplist"] == match_data["maplist"]
    assert response.data["config"]["num_maps"] == 3


@pytest.mark.django_db
def test_create_match_with_server_offline(
    client_with_api_key, match_data, server, mocker
):
    match_data["server_id"] = server.pk
    mocker.patch.object(Server, "check_online", return_value=False)
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Server is not online. Cannot create match"


@pytest.mark.django_db
def test_create_match_with_invalid_server(client_with_api_key, match_data):
    match_data["server_id"] = 999
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "No Server matches the given query."


@pytest.mark.django_db
@pytest.mark.parametrize("match_status", [MatchStatus.LIVE, MatchStatus.STARTED])
def test_create_match_with_not_available_server(
    client_with_api_key, match_with_server, match_data, server, match_status, mocker
):
    match_with_server.status = match_status
    match_with_server.save()
    match_data["server_id"] = server.pk
    mocker.patch.object(Server, "check_online", return_value=True)
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["message"]
        == "Server is not available for a match. Another match is already running"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("with_server", [True, False])
def test_create_match_with_invalid_discord_users(
    client_with_api_key, match_data, with_server, server, mocker
):
    invalid_users = [2444122323, 22, 33, 445]
    match_data["discord_users_ids"] = invalid_users
    if with_server:
        mocker.patch.object(Server, "check_online", return_value=True)
        match_data["server_id"] = server.pk
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "Discord users not found"
    for user in invalid_users:
        assert str(user) in response.data["users"]


@pytest.mark.django_db
def test_create_match_without_required_fields(client_with_api_key):
    response = client_with_api_key.post(API_ENDPOINT)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_match_with_not_enough_discord_users(
    client_with_api_key, match_data, players
):
    match_data["discord_users_ids"] = [players[0].discord_user.pk]
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "At least 2 players are required"


@pytest.mark.django_db
def test_create_match_with_invalid_author(client_with_api_key, match_data):
    author_id = 990
    match_data["author_id"] = author_id
    response = client_with_api_key.post(API_ENDPOINT, match_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "Author not found"
    assert response.data["user_id"] == str(author_id)


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()
    team1_leader = match.team1.leader
    ban_data = {
        "interaction_user_id": team1_leader.discord_user.user_id,
        "map_tag": "de_mirage",
    }
    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", ban_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["banned_map"]["tag"] == ban_data["map_tag"]
    assert response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == match.team2.leader.discord_user.user_id
    )
    assert response.data["map_bans_count"] == 1
    updated_match = Match.objects.get(id=match.pk)
    assert len(response.data["maps_left"]) == len(updated_match.maplist)
    assert "de_mirage" not in response.data["maps_left"] and match.maplist
    assert not updated_match.maps.filter(tag="de_mirage").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_pick_map(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()
    team1_leader = match.team1.leader
    team2_leader = match.team2.leader
    team1_ban_data = {
        "interaction_user_id": team1_leader.discord_user.user_id,
        "map_tag": "de_nuke",
    }
    team1_ban_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data
    )
    assert team1_ban_response.status_code == status.HTTP_200_OK
    team2_ban_data = {
        "interaction_user_id": team2_leader.discord_user.user_id,
        "map_tag": "de_overpass",
    }
    team2_ban_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data
    )
    assert team2_ban_response.status_code == status.HTTP_200_OK
    pick_data = {
        "interaction_user_id": team1_leader.discord_user.user_id,
        "map_tag": "de_mirage",
    }
    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/pick/", pick_data)
    if match_type == MatchType.BO1:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Cannot pick a map in a BO1 match"
        return
    assert response.status_code == status.HTTP_200_OK
    assert response.data["picked_map"]["tag"] == pick_data["map_tag"]
    assert response.data["next_pick_team"]["name"] == match.team2.name
    assert (
        response.data["next_pick_team"]["leader"]["discord_user"]["user_id"]
        == match.team2.leader.discord_user.user_id
    )
    assert response.data["map_picks_count"] == 1
    assert [
        team1_ban_data["map_tag"],
        team2_ban_data["map_tag"],
        pick_data["map_tag"],
    ] not in response.data["maps_left"]


@pytest.mark.django_db
def test_match_b01_map_veto_flow(client_with_api_key, match):
    match.type = MatchType.BO1
    match.save()

    team1_leader = match.team1.leader
    team2_leader = match.team2.leader

    end_map_should_left = "de_vertigo"
    team1_ban_data = [
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_anubis",
        },
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_overpass",
        },
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_nuke",
        },
    ]

    team2_ban_data = [
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_mirage",
        },
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_ancient",
        },
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_inferno",
        },
    ]

    # First team 1 ban
    t1_ban_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data[0]
    )
    assert t1_ban_1_response.status_code == status.HTTP_200_OK
    assert t1_ban_1_response.data["banned_map"]["tag"] == team1_ban_data[0]["map_tag"]
    assert len(t1_ban_1_response.data["maps_left"]) == 6
    assert t1_ban_1_response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        t1_ban_1_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # First team 2 ban
    t2_ban_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data[0]
    )
    assert t2_ban_1_response.status_code == status.HTTP_200_OK
    assert t2_ban_1_response.data["banned_map"]["tag"] == team2_ban_data[0]["map_tag"]
    assert len(t2_ban_1_response.data["maps_left"]) == 5
    assert t2_ban_1_response.data["next_ban_team"]["name"] == match.team1.name
    assert (
        t2_ban_1_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    # Second team 1 ban
    t1_ban_2_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data[1]
    )
    assert t1_ban_2_response.status_code == status.HTTP_200_OK
    assert t1_ban_2_response.data["banned_map"]["tag"] == team1_ban_data[1]["map_tag"]
    assert len(t1_ban_2_response.data["maps_left"]) == 4
    assert t1_ban_2_response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        t1_ban_2_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # Second team 2 ban
    t2_ban_2_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data[1]
    )
    assert t2_ban_2_response.status_code == status.HTTP_200_OK
    assert t2_ban_2_response.data["banned_map"]["tag"] == team2_ban_data[1]["map_tag"]
    assert len(t2_ban_2_response.data["maps_left"]) == 3
    assert t2_ban_2_response.data["next_ban_team"]["name"] == match.team1.name
    assert (
        t2_ban_2_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    # Third team 1 ban
    t1_ban_3_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data[2]
    )
    assert t1_ban_3_response.status_code == status.HTTP_200_OK
    assert t1_ban_3_response.data["banned_map"]["tag"] == team1_ban_data[2]["map_tag"]
    assert len(t1_ban_3_response.data["maps_left"]) == 2
    assert t1_ban_3_response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        t1_ban_3_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # Third team 2 ban
    t2_ban_3_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data[2]
    )
    assert t2_ban_3_response.status_code == status.HTTP_200_OK
    assert t2_ban_3_response.data["banned_map"]["tag"] == team2_ban_data[2]["map_tag"]
    assert len(t2_ban_3_response.data["maps_left"]) == 1
    assert t2_ban_3_response.data["next_ban_team"]["name"] == match.team1.name
    assert (
        t2_ban_3_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    assert t2_ban_3_response.data["maps_left"][0] == end_map_should_left


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map_with_first_team2(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()

    team2_leader = match.team2.leader.discord_user.user_id

    data = {"interaction_user_id": team2_leader, "map_tag": "de_mirage"}

    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map_with_already_banned_map(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()

    team_leader = match.team1.leader.discord_user.user_id
    data = {"interaction_user_id": team_leader, "map_tag": "de_mirage"}
    already_ban_msg = f'Map {data["map_tag"]} already banned'

    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)

    assert response.status_code == status.HTTP_200_OK

    response2 = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.data["message"] == already_ban_msg

    data["interaction_user_id"] = match.team2.leader.discord_user.user_id

    response3 = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response3.status_code == status.HTTP_400_BAD_REQUEST
    assert response3.data["message"] == already_ban_msg


@pytest.mark.django_db
@pytest.mark.skip
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map_with_invalid_team_leader(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()
    team_leader = match.team1.players.first().discord_user.user_id
    data = {"interaction_user_id": team_leader, "map_tag": "de_mirage"}

    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map_two_times_in_row(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()
    team_leader = match.team1.leader.discord_user.user_id

    data = {"interaction_user_id": team_leader, "map_tag": "de_mirage"}

    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response.status_code == status.HTTP_200_OK

    data["map_tag"] = "de_nuke"

    response2 = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("match_type", [MatchType.BO1, MatchType.BO3])
def test_match_ban_map_first_team2(client_with_api_key, match, match_type):
    match.type = match_type
    match.save()

    team_leader = match.team2.leader.discord_user.user_id

    data = {"interaction_user_id": team_leader, "map_tag": "de_mirage"}

    response = client_with_api_key.post(f"{API_ENDPOINT}{match.pk}/ban/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_match_b03_map_veto_flow(client_with_api_key, match):
    match.type = MatchType.BO3
    match.save()

    team1_leader = match.team1.leader
    team2_leader = match.team2.leader

    end_maps_should_left = ["de_nuke", "de_mirage", "de_vertigo"]
    team1_ban_data = [
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_anubis",
        },
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_overpass",
        },
    ]

    team1_pick_data = [
        {
            "interaction_user_id": team1_leader.discord_user.user_id,
            "map_tag": "de_nuke",
        },
    ]

    team2_ban_data = [
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_ancient",
        },
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_inferno",
        },
    ]

    team2_pick_data = [
        {
            "interaction_user_id": team2_leader.discord_user.user_id,
            "map_tag": "de_mirage",
        },
    ]

    # First team 1 ban
    t1_ban_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data[0]
    )
    assert t1_ban_1_response.status_code == status.HTTP_200_OK
    assert t1_ban_1_response.data["banned_map"]["tag"] == team1_ban_data[0]["map_tag"]
    assert len(t1_ban_1_response.data["maps_left"]) == 6
    assert t1_ban_1_response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        t1_ban_1_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # First team 2 ban
    t2_ban_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data[0]
    )
    assert t2_ban_1_response.status_code == status.HTTP_200_OK
    assert t2_ban_1_response.data["banned_map"]["tag"] == team2_ban_data[0]["map_tag"]
    assert len(t2_ban_1_response.data["maps_left"]) == 5
    assert t2_ban_1_response.data["next_ban_team"]["name"] == match.team1.name
    assert (
        t2_ban_1_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    # First team 1 pick
    t1_pick_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/pick/", team1_pick_data[0]
    )
    assert t1_pick_1_response.status_code == status.HTTP_200_OK
    assert t1_pick_1_response.data["picked_map"]["tag"] == team1_pick_data[0]["map_tag"]
    assert len(t1_pick_1_response.data["maps_left"]) == 4
    assert t1_pick_1_response.data["map_picks_count"] == 1
    assert t1_pick_1_response.data["next_pick_team"]["name"] == match.team2.name
    assert (
        t1_pick_1_response.data["next_pick_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # First team 2 pick
    t2_pick_1_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/pick/", team2_pick_data[0]
    )
    assert t2_pick_1_response.status_code == status.HTTP_200_OK
    assert t2_pick_1_response.data["picked_map"]["tag"] == team2_pick_data[0]["map_tag"]
    assert len(t2_pick_1_response.data["maps_left"]) == 3
    assert t2_pick_1_response.data["map_picks_count"] == 2
    assert t2_pick_1_response.data["next_pick_team"]["name"] == match.team1.name
    assert (
        t2_pick_1_response.data["next_pick_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    # Second team 1 ban
    t1_ban_2_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team1_ban_data[1]
    )
    assert t1_ban_2_response.status_code == status.HTTP_200_OK
    assert t1_ban_2_response.data["banned_map"]["tag"] == team1_ban_data[1]["map_tag"]
    assert len(t1_ban_2_response.data["maps_left"]) == 2
    assert t1_ban_2_response.data["next_ban_team"]["name"] == match.team2.name
    assert (
        t1_ban_2_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team2_leader.discord_user.user_id
    )

    # Second team 2 ban
    t2_ban_2_response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/ban/", team2_ban_data[1]
    )
    assert t2_ban_2_response.status_code == status.HTTP_200_OK
    assert t2_ban_2_response.data["banned_map"]["tag"] == team2_ban_data[1]["map_tag"]
    assert len(t2_ban_2_response.data["maps_left"]) == 1
    assert t2_ban_2_response.data["next_ban_team"]["name"] == match.team1.name
    assert (
        t2_ban_2_response.data["next_ban_team"]["leader"]["discord_user"]["user_id"]
        == team1_leader.discord_user.user_id
    )

    assert len(t2_ban_2_response.data["maps_left"]) == 1
    assert t2_ban_2_response.data["maps_left"][0] == end_maps_should_left[2]

    updated_match = Match.objects.get(id=match.pk)
    assert updated_match.maplist == end_maps_should_left


@pytest.mark.django_db
def test_get_match_config(client_with_token, match):
    response = client_with_token.get(f"{API_ENDPOINT}{match.pk}/config/")
    assert response.status_code == status.HTTP_200_OK
    match_config = match.get_config()
    match_config["matchid"] = str(match_config["matchid"])
    assert response.data == match_config


@pytest.mark.django_db
def test_match_shuffle(client_with_api_key, match):
    response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/shuffle/",
        data={"interaction_user_id": match.author.user_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["maplist"] == match.maplist
    assert response.data["team1"]["players"] != match.team1.get_players_dict()
    assert response.data["team2"]["players"] != match.team2.get_players_dict()


@pytest.mark.django_db
def test_match_shuffle_with_invalid_author(client_with_api_key, match):
    response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/shuffle/",
        data={"interaction_user_id": match.team2.leader.discord_user.user_id},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("with_server", [True, False])
def test_match_recreate(client_with_api_key, match, match_with_server, with_server):
    match_to_test = match if not with_server else match_with_server
    response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/recreate/",
        data={"interaction_user_id": match.author.user_id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == MatchStatus.CREATED
    assert response.data["type"] == match_to_test.type
    assert response.data["author"]["user_id"] == match_to_test.author.user_id
    assert response.data["team1"]["id"] == match_to_test.team1.pk
    assert response.data["team2"]["name"] == match_to_test.team2.name
    assert response.data["team2"]["id"] == match_to_test.team2.pk
    assert response.data["players_per_team"] == match_to_test.players_per_team
    assert response.data["clinch_series"] == match_to_test.clinch_series
    assert response.data["map_sides"] == match_to_test.map_sides
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None


@pytest.mark.django_db
def test_match_recreate_with_invalid_author(client_with_api_key, match):
    response = client_with_api_key.post(
        f"{API_ENDPOINT}{match.pk}/recreate/",
        data={"interaction_user_id": match.team2.leader.discord_user.user_id},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_match(client_with_api_key, match):
    response = client_with_api_key.delete(f"{API_ENDPOINT}{match.pk}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Match.objects.filter(pk=match.pk).exists()


@pytest.mark.django_db
def test_update_match(client_with_api_key, match, server):
    type = MatchType.BO3
    clinch_series = True
    map_sides = ["knife", "team1_ct", "team2_t"]
    team1_id = match.team2.id
    team2_id = match.team1.id
    cvars = {"sv_cheats": "1"}
    message_id = "123"
    server_id = server.pk
    data = {
        "type": type,
        "clinch_series": clinch_series,
        "map_sides": map_sides,
        "team1_id": team1_id,
        "team2_id": team2_id,
        "cvars": cvars,
        "message_id": message_id,
        "server_id": server_id,
    }
    response = client_with_api_key.put(f"{API_ENDPOINT}{match.pk}/", data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["type"] == type
    assert response.data["clinch_series"] == clinch_series
    assert response.data["map_sides"] == map_sides
    assert response.data["team1"]["id"] == team1_id
    assert response.data["team2"]["id"] == team2_id
    assert response.data["cvars"] == cvars
    assert response.data["message_id"] == message_id
    assert response.data["server"]["id"] == server_id
