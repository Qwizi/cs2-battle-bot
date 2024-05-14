from rest_framework import serializers

from accounts.serializers import UserSerializer
from guilds.models import Guild, EmbedField, Embed


class GuildSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Guild
        fields = "__all__"


class CreateGuildSerializer(serializers.Serializer):
    name = serializers.CharField()
    guild_id = serializers.CharField()
    owner_id = serializers.CharField()
    owner_username = serializers.CharField()


class UpdateGuildSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    lobby_channel = serializers.CharField(required=False)
    team1_channel = serializers.CharField(required=False)
    team2_channel = serializers.CharField(required=False)


class EmbedFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbedField
        fields = ["name", "value", "inline"]


class EmbedSerializer(serializers.ModelSerializer):
    fields = EmbedFieldSerializer(many=True)

    class Meta:
        model = Embed
        fields = [
            "title",
            "description",
            "color",
            "footer",
            "image",
            "thumbnail",
            "author",
            "fields",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Sort the fields by the 'order' attribute
        representation["fields"] = sorted(instance.fields.all(), key=lambda x: x.order)
        # Serialize the sorted fields
        representation["fields"] = EmbedFieldSerializer(
            representation["fields"], many=True
        ).data
        return representation
