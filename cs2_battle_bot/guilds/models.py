from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from prefix_id.field import PrefixIDField

from embeds.models import Embed, EmbedField


class Guild(models.Model):
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

    def create_config_embed(self):
        embed = Embed.objects.create(
            title=f"Guild configuration {self.name}",
            author=self.owner.socialaccount_set.get(provider="discord").extra_data["username"],
        )
        fields = [
            EmbedField.objects.create(
                name="Lobby Channel", value=f"@<{self.lobby_channel}>"
            ),
            EmbedField.objects.create(
                name="Team 1 Channel", value=f"@<{self.team1_channel}>"
            ),
            EmbedField.objects.create(
                name="Team 2 Channel", value=f"@<{self.team2_channel}>"
            ),
        ]
        embed.fields.set(fields)
        self.embed = embed
        self.save()
        return embed


@receiver(post_save, sender=Guild)
def create_guild(sender, instance, created, **kwargs):
    if created:
        instance.create_config_embed()
    else:
        instance.embed.title = f"Guild configuration {instance.name}"
        instance.embed.author = instance.owner.socialaccount_set.get(provider="discord").extra_data["username"]
        instance.embed.save()
        instance.embed.fields.get(
            name="Lobby Channel"
        ).value = f"@<{instance.lobby_channel}>"
        instance.embed.fields.get(
            name="Team 1 Channel"
        ).value = f"@<{instance.team1_channel}>"
        instance.embed.fields.get(
            name="Team 2 Channel"
        ).value = f"@<{instance.team2_channel}>"
        instance.embed.save()
