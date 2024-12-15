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
