from django.db import models
from prefix_id import PrefixIDField

from core.models import DateMixin

class Map(DateMixin):
    id = PrefixIDField(prefix="map", primary_key=True)
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.name