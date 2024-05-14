from django.db import models
from prefix_id import PrefixIDField


# Create your models here.
class DiscordUser(models.Model):
    id = PrefixIDField(primary_key=True, prefix="dc_user")
    user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.id} - {self.user_id} - {self.username}>"


class SteamUser(models.Model):
    id = PrefixIDField(primary_key=True, prefix="steam_user")
    username = models.CharField(max_length=255)
    steamid64 = models.CharField(max_length=255, null=True)
    steamid32 = models.CharField(max_length=255, null=True)
    profile_url = models.CharField(max_length=255, null=True)
    avatar = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.id} - {self.steamid64} - {self.username}>"


class Player(models.Model):
    id = PrefixIDField(primary_key=True, prefix="player")
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    steam_user = models.ForeignKey(
        SteamUser, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"<{self.id} - {self.discord_user.username} - {self.steam_user.username}>"
            if self.steam_user
            else f"<{self.id} - {self.discord_user.username}>"
        )


class Team(models.Model):
    id = PrefixIDField(primary_key=True, prefix="team")
    name = models.CharField(max_length=255)
    players = models.ManyToManyField("players.Player", related_name="teams")
    leader = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE,
        related_name="team_leader",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.id} - {self.name}>"

    def get_players_dict(self):
        return {
            str(player.steam_user.steamid64): player.steam_user.username
            for player in self.players.all()
        }
