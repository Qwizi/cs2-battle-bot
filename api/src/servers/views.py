from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from servers.models import Server
from servers.serializers import ServerSerializer


class CustomSchemeRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = ["steam"]


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all().order_by("created_at")
    serializer_class = ServerSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="guild_or_public",
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        guild_or_public = self.request.query_params.get("guild_or_public")

        if guild_or_public:
            return Server.objects.filter(
                Q(is_public=True) | Q(guild__id=guild_or_public)
            ).order_by("created_at")
        else:
            # No filters applied, return original queryset
            return Server.objects.all().order_by("created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=True, methods=["GET"], permission_classes=[AllowAny])
    def join(self, request, pk=None):
        server = self.get_object()
        return CustomSchemeRedirect(server.get_join_link())
