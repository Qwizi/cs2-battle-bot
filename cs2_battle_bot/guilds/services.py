from django.contrib.auth import get_user_model

from guilds.models import Guild

User = get_user_model()


async def create_guild_if_not_exists(owner_username, guild_id, guild_name):
    owner_username = owner_username
    user, user_created = await User.objects.aget_or_create(
        username=owner_username,
        defaults={'email': '', 'password': None}
    )
    if user_created:
        print(f"Created user for {owner_username}")
    else:
        print(f"User exists for {owner_username}")

    guild_created, created = await Guild.objects.aget_or_create(
        guild_id=guild_id,
        defaults={'owner': user, 'name': guild_name}
    )
    if created:
        print(f"Created guild for {guild_name}")
    return owner_username, guild_id, guild_name
