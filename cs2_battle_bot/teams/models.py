from django.db import models
from prefix_id import PrefixIDField


class Team(models.Model):
    id = PrefixIDField(prefix="team", primary_key=True)
    name = models.CharField(max_length=255)
    players = models.ManyToManyField("accounts.Account", related_name="teams")
    guild = models.ForeignKey("guilds.Guild", on_delete=models.CASCADE, related_name="teams")

    def __str__(self):
        return self.name
