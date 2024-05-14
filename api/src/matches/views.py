from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.auth import BearerTokenAuthentication
from guilds.models import Guild
from matches.models import (
    Map,
    Match,
)
from matches.permissions import IsAuthor
from matches.serializers import (
    MapBanSerializer,
    MapSerializer,
    MatchConfigSerializer,
    MatchMapSelectedSerializer,
    MatchSerializer,
    CreateMatchSerializer,
    MatchBanMapSerializer,
    MatchPickMapSerializer,
    MatchBanMapResultSerializer,
    MatchPickMapResultSerializer,
    InteractionUserSerializer,
    MatchUpdateSerializer,
    MatchPlayerJoin,
    MatchPlayerLeave,
    MatchSelectCaptain,
)
from matches.utils import (
    ban_map,
    create_match,
    join_match,
    load_match,
    pick_map,
    process_webhook,
    recreate_match,
    shuffle_teams,
    leave_match,
    select_captain,
)
from players.models import Team, DiscordUser
from servers.models import Server


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all().order_by("created_at")
    serializer_class = MatchSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(request=CreateMatchSerializer, responses={201: MatchSerializer})
    def create(self, request, *args, **kwargs):
        return create_match(request)

    @extend_schema(request=MatchUpdateSerializer, responses={200: MatchSerializer})
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data.get("status"):
            instance.status = data["status"]
        if data.get("type"):
            instance.type = data["type"]
        if data.get("team1_id"):
            instance.team1 = get_object_or_404(Team, id=data["team1_id"])
        if data.get("team2_id"):
            instance.team2 = get_object_or_404(Team, id=data["team2_id"])
        if data.get("map_sides"):
            instance.map_sides = data["map_sides"]
        if data.get("clinch_series"):
            instance.clinch_series = data["clinch_series"]
        if data.get("cvars"):
            instance.cvars = data["cvars"]
        if data.get("message_id"):
            instance.message_id = data["message_id"]
        if data.get("author_id"):
            instance.author = get_object_or_404(DiscordUser, id=data["author_id"])
        if data.get("server_id"):
            instance.server = get_object_or_404(Server, id=data["server_id"])
        if data.get("guild_id"):
            instance.guild = get_object_or_404(Guild, id=data["guild_id"])
        instance.save()
        return Response(self.get_serializer(instance).data, status=200)

    @action(detail=True, methods=["POST"])
    def load(self, request, pk=None):
        return load_match(pk, request)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated, IsAuthor],
        authentication_classes=[BearerTokenAuthentication],
    )
    def webhook(self, request, pk):
        return process_webhook(request, pk)

    @extend_schema(
        request=MatchBanMapSerializer, responses={200: MatchBanMapResultSerializer}
    )
    @action(detail=True, methods=["POST"])
    def ban(self, request, pk):
        return ban_map(request, pk)

    @extend_schema(
        request=MatchPickMapSerializer, responses={200: MatchPickMapResultSerializer}
    )
    @action(detail=True, methods=["POST"])
    def pick(self, request, pk):
        return pick_map(request, pk)

    @action(detail=True, methods=["POST"])
    def recreate(self, request, pk):
        return recreate_match(request, pk)

    @extend_schema(request=InteractionUserSerializer, responses={200: MatchSerializer})
    @action(detail=True, methods=["POST"])
    def shuffle(self, request, pk):
        return shuffle_teams(request, pk)

    @extend_schema(responses={200: MapBanSerializer(many=True)})
    @action(detail=True, methods=["GET"])
    def bans(self, request, pk):
        match: Match = self.get_object()
        queryset = match.map_bans.all().order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MapBanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MapBanSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: MatchMapSelectedSerializer(many=True)})
    @action(detail=True, methods=["GET"])
    def picks(self, request, pk):
        match: Match = self.get_object()
        queryset = match.map_picks.all().order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MatchMapSelectedSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MatchMapSelectedSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=MatchPlayerJoin, responses={200: MatchSerializer})
    @action(detail=True, methods=["POST"])
    def join(self, request, pk):
        return join_match(request, pk)

    @extend_schema(request=MatchPlayerLeave, responses={200: MatchSerializer})
    @action(detail=True, methods=["POST"])
    def leave(self, request, pk):
        return leave_match(request, pk)

    @extend_schema(request=MatchSelectCaptain, responses={200: MatchSerializer})
    @action(detail=True, methods=["POST"])
    def captain(self, request, pk):
        return select_captain(request, pk)

    @extend_schema(responses={200: MatchConfigSerializer})
    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsAuthor],
        authentication_classes=[BearerTokenAuthentication],
    )
    def config(self, request, pk):
        match = self.get_object()
        serializer = MatchConfigSerializer(data=match.get_config())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        return Response(serializer.data, status=200)


class MapViewSet(viewsets.ModelViewSet):
    queryset = Map.objects.all().order_by("created_at")
    serializer_class = MapSerializer
