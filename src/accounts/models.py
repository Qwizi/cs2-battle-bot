from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group


from django.db import models
from prefix_id import PrefixIDField



# Create your models here.

class Account(AbstractUser, PermissionsMixin):
    id = PrefixIDField(prefix="account", primary_key=True)
    short_id = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='account_set',
        related_query_name='account',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='account_set',
        related_query_name='account',
        verbose_name='user permissions'
    )

    class Meta:
        ordering = ['date_joined']

    def get_steam_account(self):
        return self.socialaccount_set.filter(provider='steam').first()

    def get_discord_account(self):
        return self.socialaccount_set.filter(provider='discord').first()

    def have_steam_account(self):
        return self.socialaccount_set.filter(provider='steam').exists()

    def have_discord_account(self):
        return self.socialaccount_set.filter(provider='discord').exists()


    def get_discord_avatar(self):
        dc_account = self.socialaccount_set.filter(provider='discord').first()
        if not dc_account:
            return None

        avatar = dc_account.extra_data.get('avatar')
        user_id = dc_account.uid
        discriminator = dc_account.extra_data.get('discriminator')

        if avatar:
            # User has custom avatar
            return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png"
        else:
            # Use default avatar (based on discriminator or ID mod 5 if discriminator not available)
            try:
                index = int(discriminator) % 5 if discriminator else int(user_id) % 5
            except (ValueError, TypeError):
                index = 0  # fallback
            return f"https://cdn.discordapp.com/embed/avatars/{index}.png"

    def get_avatar(self):
        if self.socialaccount_set.filter(provider='discord').exists():
            return self.get_discord_avatar()
        return None
