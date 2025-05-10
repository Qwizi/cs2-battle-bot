import typing

import pydantic
from django.db import models
from django_pydantic_field import SchemaField
from prefix_id import PrefixIDField

from core.models import DateMixin
from matches.pydantic_schemas import MapBan, MapList, MatchConfigJSON, MatchConfigSpecJSON


class Match(DateMixin):

    class Status(models.TextChoices):
        CREATED = 'created'
        MAP_VETO_STARTED = 'map_veto_started'
        MAP_VETO_ENDED = 'map_veto_ended'
        LIVE = 'live'
        CANCELLED = 'cancelled'
        FINISHED = 'finished'


    class Type(models.TextChoices):
        BO1 = 'bo1'
        BO3 = 'bo3'
        BO5 = 'bo5'

    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.CREATED)
    config = models.ForeignKey('matches.MatchConfig', on_delete=models.CASCADE, related_name='matches', default=None)
    team1 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team1_matches', default=None)
    team2 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team2_matches', default=None)
    map_bans: MapBan = SchemaField()
    map_list: MapList = SchemaField()
    map_veto_state = models.JSONField(default=dict)
    guild = models.ForeignKey('guilds.Guild', on_delete=models.CASCADE, related_name='matches', default=None)

    def __str__(self):
        return self.name

    def get_status(self):
        return self.status

    def get_json_config(self):
        num_maps = 1
        if self.config.type == Match.Type.BO3:
            num_maps = 3
        elif self.config.type == Match.Type.BO5:
            num_maps = 5
        return MatchConfigJSON(
            match_id=self.id,
            team1=self.team1.get_config(),
            team2=self.team2.get_config(),
            num_maps=num_maps,
            maplist=[_map.tag for _map in self.map_list],
            map_sides=self.config.map_sides,
            spectators=MatchConfigSpecJSON(players={}),
            clinch_series=self.config.clinch_series,
            players_per_team=self.config.players_per_team,
            cvars=self.config.cvars
        )

class MatchConfig(DateMixin):
    class GameMode(models.TextChoices):
        COMPETITIVE = 'competitive'
        WINGMAN = 'wingman'

    id = PrefixIDField(prefix="matchconfig", primary_key=True)
    name = models.CharField(max_length=100)
    game_mode = models.CharField(max_length=100, choices=GameMode.choices, default=GameMode.COMPETITIVE)
    type = models.CharField(max_length=100, choices=Match.Type.choices, default=Match.Type.BO1)
    map_sides = models.JSONField(default=dict)
    players_per_team = models.IntegerField(default=5)
    shuffle_teams = models.BooleanField(default=False)
    clinch_series = models.BooleanField(default=False)
    cvars = models.JSONField(default=dict)
    guild = models.ForeignKey('guilds.Guild', on_delete=models.CASCADE, related_name='match_configs', default=None, null=True, blank=True)