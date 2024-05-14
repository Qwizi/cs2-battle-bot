from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from prefix_id import PrefixIDField
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    id = PrefixIDField(primary_key=True, prefix="user")
    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, null=True, blank=True
    )

    REQUIRED_FIELDS = []

    def get_token(self):
        return Token.objects.get(user=self).key


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
