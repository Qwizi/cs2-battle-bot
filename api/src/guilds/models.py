from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from prefix_id import PrefixIDField

from players.models import DiscordUser, Player

UserModel = get_user_model()


class EmbedField(models.Model):
    id = PrefixIDField(primary_key=True, prefix="embed_field")
    order = models.IntegerField(default=1)
    name = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    inline = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Embed(models.Model):
    id = PrefixIDField(primary_key=True, prefix="embed")
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    footer = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    fields = models.ManyToManyField(EmbedField, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Create your models here.


class GuildManager(models.Manager):
    def create_guild(self, owner_id: str, owner_username: str, **kwargs):
        dc_owner_user, _ = DiscordUser.objects.get_or_create(
            user_id=owner_id, username=owner_username
        )
        player, _ = Player.objects.get_or_create(discord_user=dc_owner_user)
        owner_user, _ = UserModel.objects.get_or_create(username=owner_username)
        if not owner_user.player:
            owner_user.player = player
            owner_user.save()
        guild = self.create(owner=owner_user, **kwargs)
        guild.save()
        return guild


class Guild(models.Model):
    objects = GuildManager()
    id = PrefixIDField(primary_key=True, prefix="guild")
    name = models.CharField(max_length=255)
    guild_id = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guild_owner"
    )
    lobby_channel = models.CharField(max_length=255, null=True, blank=True)
    team1_channel = models.CharField(max_length=255, null=True, blank=True)
    team2_channel = models.CharField(max_length=255, null=True, blank=True)
    embed = models.ForeignKey(Embed, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Guild)
def create_guild(sender, instance, created, **kwargs):
    if created:
        embed = Embed.objects.create(
            title=f"Guild configuration {instance.name}",
            author=instance.owner.player.discord_user.username,
        )
        fields = [
            EmbedField.objects.create(
                name="Lobby Channel", value=f"@<{instance.lobby_channel}"
            ),
            EmbedField.objects.create(
                name="Team 1 Channel", value=f"@<{instance.team1_channel}"
            ),
            EmbedField.objects.create(
                name="Team 2 Channel", value=f"@<{instance.team2_channel}"
            ),
        ]
        embed.fields.set(fields)
        instance.embed = embed
        instance.save()
    else:
        instance.embed.title = f"Guild configuration {instance.name}"
        instance.embed.author = instance.owner.player.discord_user.username
        instance.embed.save()
        instance.embed.fields.get(
            name="Lobby Channel"
        ).value = f"@<{instance.lobby_channel}"
        instance.embed.fields.get(
            name="Team 1 Channel"
        ).value = f"@<{instance.team1_channel}"
        instance.embed.fields.get(
            name="Team 2 Channel"
        ).value = f"@<{instance.team2_channel}"
        instance.embed.save()
