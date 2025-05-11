from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver
from loguru import logger
from prefix_id import PrefixIDField
from asgiref.sync import sync_to_async
from guardian.shortcuts import assign_perm
from core.models import DateMixin

User = get_user_model()


class Guild(DateMixin):
    id = PrefixIDField(prefix="guild", primary_key=True)
    gid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='guilds', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_guilds', blank=True, null=True)
    lobby_channel = models.CharField(max_length=100, blank=True, null=True)
    team1_channel = models.CharField(max_length=100, blank=True, null=True)
    team2_channel = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


    async def is_member_dc_guild(self, user, dc_guild):
        return await self.get_member(user, dc_guild)

    async def get_member(self, user, dc_guild):
        dc_account = await user.socialaccount_set.filter(provider='discord').afirst()
        if not dc_account:
            return None
        return await dc_guild.fetch_member(dc_account.uid)

    async def sync_members(self, dc_guild):
        logger.info(f"Syncing members for guild {self.name}")
        users = [user async for user in User.objects.all()]
        logger.info(f"Found {len(users)} users in the database")
        for user in users:
            if await self.is_member_dc_guild(user, dc_guild):
                if await self.members.filter(id=user.id).aexists():
                    logger.info(f"User {user.username} is already a member of guild db {self.name}")
                    continue
                logger.info(f"User {user.username} is not a member of guild db {self.name}")

                await self.members.aadd(user)
                await self.asave()
                await sync_to_async(lambda: assign_perm('view_guild', user, self))()
                logger.info(f"Assigned view_guild permission to user {user.username} for guild {self.name}")
                logger.info(f"Added user {user.username} to guild {self.name}")
            else:
                logger.info(f"User {user.username} is not member of dc guild {dc_guild.name}")
        logger.info(f"Finished syncing members for guild {self.name}")

    async def sync_owner(self, dc_guild):
        logger.info(f"Syncing owner for guild {self.name}")
        owner = dc_guild.owner
        guild_owner = await sync_to_async(lambda: self.owner)()
        if guild_owner:
            logger.info(f"Guild {self.name} already has an owner {guild_owner.username}")
            return
        if owner:
            owner_account = await User.objects.filter(socialaccount__uid=owner.id).afirst()
            if owner_account:
                logger.info(f"Found owner {owner_account.username} in database for guild {self.name}")
                self.owner = owner_account
                await self.asave()
                logger.info(f"Set owner {owner_account.username} for guild {self.name}")
            else:
                logger.info(f"Owner {owner.id} not found in database for guild {self.name}")
        else:
            logger.info(f"No owner found for guild {self.name}")
        logger.info(f"Finished syncing owner for guild {self.name}")
