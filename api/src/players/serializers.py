from players.models import Player, Team, DiscordUser, SteamUser
from rest_framework import serializers


class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = "__all__"


class SteamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SteamUser
        fields = "__all__"


class PlayerSerializer(serializers.ModelSerializer):
    discord_user = DiscordUserSerializer()
    steam_user = SteamUserSerializer(allow_null=True)

    class Meta:
        model = Player
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    leader = PlayerSerializer()

    class Meta:
        model = Team
        fields = "__all__"
