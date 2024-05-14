from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from guilds.models import Guild
from guilds.serializers import (
    GuildSerializer,
    CreateGuildSerializer,
    UpdateGuildSerializer,
)
from guilds.utils import create_guild


class GuildViewSet(viewsets.ModelViewSet):
    queryset = Guild.objects.all().order_by("created_at")
    serializer_class = GuildSerializer
    lookup_field = "guild_id"

    @extend_schema(request=CreateGuildSerializer, responses={201: GuildSerializer})
    def create(self, request, *args, **kwargs):
        return create_guild(request)

    @extend_schema(request=UpdateGuildSerializer, responses={200: GuildSerializer})
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateGuildSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        if data.get("name"):
            instance.name = data["name"]
        if data.get("lobby_channel"):
            instance.lobby_channel = data["lobby_channel"]
        if data.get("team1_channel"):
            instance.team1_channel = data["team1_channel"]
        if data.get("team2_channel"):
            instance.team2_channel = data["team2_channel"]
        instance.save()
        return Response(self.get_serializer(instance).data)
