import pytest
from rest_framework import status


from players.models import Team

API_URL = "/api/teams/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "patch", "delete"])
def test_teams_unauthorized(methods, api_client):
    team = Team.objects.create(name="Team 1")

    if methods == "get":
        response = api_client.get(API_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response2 = api_client.get(f"{API_URL}{team.id}/")
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_URL, data={"name": "Team 2"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_URL}{team.id}/", data={"name": "Team 3"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "patch":
        response = api_client.patch(f"{API_URL}{team.id}/", data={"name": "Team 4"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_URL}{team.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_teams_empty_list(client_with_api_key):
    response = client_with_api_key.get(API_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_teams_list(client_with_api_key):
    team = Team.objects.create(name="Team 1")
    response = client_with_api_key.get(API_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Team 1"
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_team(client_with_api_key):
    team = Team.objects.create(name="Team 1")
    response = client_with_api_key.get(f"{API_URL}{team.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Team 1"
    assert response.data["leader"] is None
    assert response.data["players"] == []
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None


@pytest.mark.django_db
@pytest.mark.skip
def test_create_team(client_with_api_key):
    response = client_with_api_key.post(API_URL, data={"name": "Team 1"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Team 1"
    assert response.data["leader"] is None
    assert response.data["players"] == []
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None


@pytest.mark.django_db
@pytest.mark.skip
def test_delete_team(client_with_api_key):
    team = Team.objects.create(name="Team 1")
    response = client_with_api_key.delete(f"{API_URL}{team.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Team.objects.count() == 0
