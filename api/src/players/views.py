from rest_framework import viewsets
from players.models import Player, Team, DiscordUser, SteamUser
from players.serializers import (
    PlayerSerializer,
    TeamSerializer,
    DiscordUserSerializer,
    SteamUserSerializer,
)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all().order_by("created_at")
    serializer_class = PlayerSerializer


class DiscordUserViewSet(viewsets.ModelViewSet):
    queryset = DiscordUser.objects.all().order_by("created_at")
    serializer_class = DiscordUserSerializer


class SteamUserViewSet(viewsets.ModelViewSet):
    queryset = SteamUser.objects.all().order_by("created_at")
    serializer_class = SteamUserSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all().order_by("created_at")
    serializer_class = TeamSerializer
