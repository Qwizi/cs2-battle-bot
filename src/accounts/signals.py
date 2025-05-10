from allauth.socialaccount.signals import social_account_added, social_account_updated
from allauth.socialaccount.models import SocialToken
from django.dispatch import receiver
from loguru import logger
import requests

from guilds.models import Guild


@receiver([social_account_added, social_account_updated])
def fetch_discord_data(request, sociallogin, **kwargs):
    
    if sociallogin.account.provider != "discord":
        return
    
    user = sociallogin.user
    logger.info(f"User {user.username} logged in with Discord")
    token = SocialToken.objects.get(account__user=user, account__provider="discord")
    headers = {"Authorization": f"Bearer {token.token}"}

    guilds_data = requests.get(
        "https://discord.com/api/users/@me/guilds", headers=headers
    ).json()
    guilds_ids = [guild["id"] for guild in guilds_data]
    owned_guilds = [g for g in guilds_data if g.get("owner")]
    logger.info(f"User {user.username} is in {len(guilds_ids)} guilds")
    logger.info(f"User {user.username} owns {len(owned_guilds)} guilds")
    # Add user to guilds

    logger.info(f"Adding user {user.username} to guilds")
    for guild_db in Guild.objects.all():
        if guild_db.gid in guilds_ids:
            guild_db.members.add(user)
            guild_db.save()
            logger.info(f"Added user {user.username} to guild {guild_db.name}")
    logger.info(f"Finished adding user {user.username} to guilds")

    logger.info(f"Setting user {user.username} as owner of guilds")
    for guild in owned_guilds:
        try:
            guild_db = Guild.objects.get(gid=guild["id"])
            if guild_db.owner:
                logger.info(f"Guild {guild_db.name} already has an owner {guild_db.owner.username}")
                continue
            guild_db.owner = user
            guild_db.save()
            logger.info(f"Set user {user.username} as owner of guild {guild_db.name}")
        except Guild.DoesNotExist:
            logger.info(f"Guild {guild['id']} does not exist in the database")
            continue

