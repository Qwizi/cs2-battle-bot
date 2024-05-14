import pytest
from django.test import RequestFactory
from rest_framework.reverse import reverse_lazy

from matches.models import Map, MatchType, Match, MapPool, MatchConfig, GameMode


@pytest.fixture
def map_data():
    return {"name": "Mirage", "tag": "de_mirage"}


@pytest.fixture(autouse=True)
def default_maps():
    maps_dict = [
        {"name": "Anubis", "tag": "de_anubis"},
        {"name": "Overpass", "tag": "de_overpass"},
        {"name": "Nuke", "tag": "de_nuke"},
        {"name": "Mirage", "tag": "de_mirage"},
        {"name": "Ancient", "tag": "de_ancient"},
        {"name": "Inferno", "tag": "de_inferno"},
        {"name": "Vertigo", "tag": "de_vertigo"},
    ]
    maps_obj = [Map.objects.get_or_create(**map) for map in maps_dict]


@pytest.fixture(autouse=True)
def default_map_pools():
    active_duty_map_pool = MapPool.objects.create(name="Competive Active Duty")
    active_duty_map_pool.maps.set(Map.objects.all())
    active_duty_map_pool.save()

    wingman_map_pool = MapPool.objects.create(name="Wingman Active Duty")
    wingman_map_pool.maps.set(
        Map.objects.filter(
            tag__in=["de_nuke", "de_inferno", "de_overpass", "de_vertigo"]
        )
    )
    wingman_map_pool.save()


configs = [
    "5v5_bo1_shuffle_teams_official",
    "5v5_bo1_official",
    "5v5_b03_shuffle_teams_official",
    "5v5_b03_official",
    "wingman_b01_official",
    "wingman_b03_official",
]


@pytest.fixture(autouse=True)
def default_match_configs():
    active_duty_map_pool = MapPool.objects.get(name="Competive Active Duty")
    wingman_map_pool = MapPool.objects.get(name="Wingman Active Duty")

    MatchConfig.objects.create(
        name=configs[0],
        game_mode=GameMode.COMPETITIVE,
        type=MatchType.BO1,
        clinch_series=False,
        max_players=10,
        shuffle_teams=True,
        map_pool=active_duty_map_pool,
    )

    MatchConfig.objects.create(
        name=configs[1],
        game_mode=GameMode.COMPETITIVE,
        type=MatchType.BO1,
        clinch_series=False,
        max_players=10,
        map_pool=active_duty_map_pool,
    )

    MatchConfig.objects.create(
        name=configs[2],
        game_mode=GameMode.COMPETITIVE,
        type=MatchType.BO3,
        clinch_series=False,
        max_players=10,
        shuffle_teams=True,
        map_pool=active_duty_map_pool,
    )

    MatchConfig.objects.create(
        name=configs[3],
        game_mode=GameMode.COMPETITIVE,
        type=MatchType.BO3,
        clinch_series=False,
        max_players=10,
        map_pool=active_duty_map_pool,
    )

    MatchConfig.objects.create(
        name=configs[4],
        game_mode=GameMode.WINGMAN,
        type=MatchType.BO1,
        clinch_series=False,
        max_players=4,
        map_pool=wingman_map_pool,
    )

    MatchConfig.objects.create(
        name=configs[5],
        game_mode=GameMode.WINGMAN,
        type=MatchType.BO3,
        clinch_series=False,
        max_players=4,
        map_pool=wingman_map_pool,
    )


@pytest.fixture
def match_data(default_author, guild):
    return {
        "config_name": "5v5_bo1_official",
        "author_id": default_author.player.discord_user.user_id,
        "guild_id": guild.guild_id,
    }


@pytest.fixture
def match(default_author, guild):
    factory = RequestFactory()

    # Create a request
    request = factory.get("/")
    new_match = Match.objects.create(
        config=MatchConfig.objects.get(name="5v5_bo1_official"),
        author=default_author.player.discord_user,
        guild=guild,
    )
    new_match.create_webhook_cvars(
        str(reverse_lazy("match-webhook", args=[new_match.pk], request=request))
    )
    return new_match


@pytest.fixture
def match_with_server(server, default_author, guild):
    factory = RequestFactory()

    # Create a request
    request2 = factory.get("/")
    new_match = Match.objects.create(
        config=MatchConfig.objects.get(name="5v5_bo1_official"),
        author=default_author.player.discord_user,
        guild=guild,
        server=server,
    )
    new_match.create_webhook_cvars(
        str(reverse_lazy("match-webhook", args=[new_match.pk], request=request2))
    )
    return new_match
