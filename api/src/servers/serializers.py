from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from servers.models import Server


class ServerSerializer(serializers.ModelSerializer):
    rcon_password = serializers.CharField(write_only=True, required=False)
    # guild = GuildSerializer(read_only=True)

    join_url = serializers.SerializerMethodField()

    def get_join_url(self, obj):
        return reverse_lazy(
            "server-join", args=[obj.id], request=self.context["request"]
        )

    class Meta:
        model = Server
        fields = [
            "id",
            "name",
            "ip",
            "port",
            "password",
            "is_public",
            "rcon_password",
            "guild",
            "join_url",
        ]
