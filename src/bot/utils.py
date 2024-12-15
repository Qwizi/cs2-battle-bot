from asgiref.sync import sync_to_async

from guilds.models import Guild

@sync_to_async
def guild_exists(gid):
    return Guild.objects.filter(gid=gid).exists()


@sync_to_async
def create_guild(name, gid):
    return Guild.objects.create(gid=gid)
