from django.contrib.auth import get_user_model
from rest_framework import serializers

from players.serializers import PlayerSerializer

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = UserModel
        fields = ["id", "username", "player"]


class AccountConnectLinkSerializer(serializers.Serializer):
    link = serializers.CharField()
