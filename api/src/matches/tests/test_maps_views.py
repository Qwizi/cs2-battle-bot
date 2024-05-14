import pytest
from rest_framework import status


from matches.models import Map

API_ENDPOINT = "/api/maps/"


@pytest.mark.django_db
@pytest.mark.parametrize("methods", ["get", "post", "put", "patch", "delete"])
def test_maps_unauthorized(methods, api_client):
    map = Map.objects.first()
    if methods == "get":
        response = api_client.get(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "post":
        response = api_client.post(API_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "put":
        response = api_client.put(f"{API_ENDPOINT}{map.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "patch":
        response = api_client.patch(f"{API_ENDPOINT}{map.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    elif methods == "delete":
        response = api_client.delete(f"{API_ENDPOINT}{map.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_maps_list(client_with_api_key):
    response = client_with_api_key.get(API_ENDPOINT)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == Map.objects.count()
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db
def test_get_map(client_with_api_key):
    map = Map.objects.first()
    response = client_with_api_key.get(f"{API_ENDPOINT}{map.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == map.name
    assert response.data["tag"] == map.tag
    assert response.data["id"] == map.id
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None


@pytest.mark.django_db
def test_create_map(client_with_api_key, map_data):
    response = client_with_api_key.post(API_ENDPOINT, map_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == map_data["name"]
    assert response.data["tag"] == map_data["tag"]
    assert response.data["id"] is not None
    assert response.data["created_at"] is not None
    assert response.data["updated_at"] is not None


@pytest.mark.django_db
def test_delete_map(client_with_api_key):
    response = client_with_api_key.delete(f"{API_ENDPOINT}{Map.objects.first().id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
