import pytest

from matches.models import Map


@pytest.mark.django_db
def test_map_model(map_data):
    map = Map.objects.create(**map_data)
    assert map.name == map_data["name"]
    assert map.tag == map_data["tag"]
    assert map.id is not None
