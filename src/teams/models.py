import random

from django.db import models
from prefix_id import PrefixIDField

from core.models import DateMixin
from matches.pydantic_schemas import MatchConfigTeamJSON


# Create your models here.

class Team(DateMixin):
    id = PrefixIDField(prefix="team", primary_key=True)
    name = models.CharField(max_length=100)
    players = models.ManyToManyField('accounts.Account', related_name='teams')
    capitan = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='capitan_team', default=None)
    guild = models.ForeignKey('guilds.Guild', on_delete=models.CASCADE, related_name='teams', default=None)
    is_temp = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_config(self):
        return MatchConfigTeamJSON(name=self.name, players={player.get_steam_account().uid: player.get_steam_account().extra["username"] for player in self.players.all()})