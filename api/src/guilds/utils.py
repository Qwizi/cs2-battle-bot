from django.contrib.auth import get_user_model
from rest_framework.response import Response

from guilds.models import Guild
from guilds.serializers import GuildSerializer, CreateGuildSerializer
from players.models import DiscordUser, Player

UserModel = get_user_model()


def create_discord_user(user_id: str, username: str) -> DiscordUser:
    try:
        discord_user = DiscordUser.objects.get(user_id=user_id)
    except DiscordUser.DoesNotExist:
        discord_user = DiscordUser.objects.create(user_id=user_id, username=username)
    return discord_user


def create_player(discord_user: DiscordUser) -> Player:
    try:
        player = Player.objects.get(discord_user=discord_user)
    except Player.DoesNotExist:
        player = Player.objects.create(discord_user=discord_user)
    return player


def create_user(discord_user_id: str, discord_username: str) -> UserModel:
    discord_user = create_discord_user(discord_user_id, discord_username)
    try:
        user = UserModel.objects.get(username=discord_username)
    except UserModel.DoesNotExist:
        user = UserModel.objects.create(username=discord_username)
    return user, discord_user


def create_guild(request) -> Response["GuildSerializer"]:
    serializer = CreateGuildSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    owner_id = serializer.validated_data["owner_id"]
    owner_username = serializer.validated_data["owner_username"]
    guild = Guild.objects.create_guild(
        name=serializer.validated_data["name"],
        guild_id=serializer.validated_data["guild_id"],
        owner_id=owner_id,
        owner_username=owner_username,
    )
    return Response(GuildSerializer(guild).data, status=201)
