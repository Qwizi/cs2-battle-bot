from rest_framework import serializers

from matches.exceptions import ConfigNotFound
from matches.models import MatchStatus, Map, MatchConfig
from players.exceptions import DiscordUserNotFound, PlayerNotInMatch
from players.models import DiscordUser


class ValidConfigName(object):
    def __call__(self, value):
        try:
            MatchConfig.objects.get(name=value)
        except MatchConfig.DoesNotExist:
            raise ConfigNotFound(detail=f"MatchConfig with name {value} does not exist")


class ValidDiscordUser(object):
    def __call__(self, value):
        try:
            DiscordUser.objects.get(user_id=value)
        except DiscordUser.DoesNotExist:
            raise DiscordUserNotFound(detail=f"DiscordUser @<{value}> does not exist")


class DiscordUserIsInMatch(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if (
            not match.team1.players.filter(discord_user__user_id=value).exists()
            and not match.team2.players.filter(discord_user__user_id=value).exists()
        ):
            raise PlayerNotInMatch(f"DiscordUser @<{value}> is not in a match")


class DiscordUserCanJoinMatch(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if match.status != MatchStatus.CREATED:
            raise serializers.ValidationError("Match is not in CREATED status")

        # Allow author to join match
        if match.author.user_id == value:
            return
        # if match.team1.players.filter(discord_user__user_id=value).exists() or match.team2.players.filter(
        #         discord_user__user_id=value).exists():
        #     raise serializers.ValidationError(f"DiscordUser @<{value}> is already in a match")

        if (
            match.team1.players.count() + match.team2.players.count()
        ) >= match.config.max_players:
            raise serializers.ValidationError("Match is full")

        if match.author.user_id == value and match.config.shuffle_teams:
            raise serializers.ValidationError(
                f"DiscordUser @<{value}> is author of the match and cannot join"
            )


class TeamCanBeJoined(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")

        if (
            value == "team1"
            and match.team1.players.count() >= match.config.max_players // 2
        ):
            raise serializers.ValidationError("Team1 is full")
        if (
            value == "team2"
            and match.team2.players.count() >= match.config.max_players // 2
        ):
            raise serializers.ValidationError("Team2 is full")


class DiscordUserCanLeaveMatch(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if match.status != MatchStatus.CREATED:
            raise serializers.ValidationError("Match is not in CREATED status")

        if match.author.user_id == value:
            raise serializers.ValidationError(
                f"DiscordUser @<{value}> is author of the match and cannot leave"
            )


class ValidMap(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if not Map.objects.filter(tag=value).exists():
            raise serializers.ValidationError(f"Map {value} does not exist")
        if not match.config.map_pool.maps.filter(tag=value).exists():
            raise serializers.ValidationError(f"Map {value} is not in the map pool")


class MapCanBeBanned(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if match.status != MatchStatus.MAP_VETO:
            raise serializers.ValidationError("Match is not in MAP_VETO status")

        if match.map_bans.filter(map__tag=value).exists():
            raise serializers.ValidationError(f"Map {value} is already banned")

        if match.map_picks.filter(map__tag=value).exists():
            raise serializers.ValidationError(f"Map {value} is already picked")


class DiscordUserIsCaptain(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        match = serializer_field.context.get("match")
        if match.team1.leader.user_id != value and match.team2.leader.user_id != value:
            raise serializers.ValidationError(
                f"DiscordUser @<{value}> is not a captain"
            )
