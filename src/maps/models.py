from django.db import models
from prefix_id import PrefixIDField

from core.models import DateMixin

class Map(DateMixin):
    id = PrefixIDField(prefix="map", primary_key=True)
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)
    guild = models.ForeignKey('guilds.Guild', on_delete=models.CASCADE, related_name='maps', default=None)

    def __str__(self):
        return self.name
    


class MapPool(models.Model):
    id = PrefixIDField(prefix="map_pool", primary_key=True)
    name = models.CharField(max_length=100)
    maps = models.ManyToManyField(Map, related_name='map_pools')
    guild = models.ForeignKey('guilds.Guild', on_delete=models.CASCADE, related_name='map_pools', default=None)

    def __str__(self):
        return self.name