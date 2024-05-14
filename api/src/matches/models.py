import math

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from prefix_id import PrefixIDField

from guilds.models import Embed, EmbedField
from players.models import Team, Player

UserModel = get_user_model()


class MatchStatus(models.TextChoices):
    CREATED = "CREATED"
    CAPTAINS_SELECT = "CAPTAINS_SELECT"
    MAP_VETO = "MAP_VETO"
    READY_TO_LOAD = "READY_TO_LOAD"
    LOADED = "LOADED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class MatchType(models.TextChoices):
    BO1 = "BO1"
    BO3 = "BO3"
    BO5 = "BO5"


class GameMode(models.TextChoices):
    COMPETITIVE = "COMPETITIVE"
    WINGMAN = "WINGMAN"
    AIM = "AIM"


class Map(models.Model):
    id = PrefixIDField(primary_key=True, prefix="map")
    name = models.CharField(max_length=255, unique=True)
    tag = models.CharField(max_length=255, unique=True)
    guild = models.ForeignKey(
        "guilds.Guild",
        on_delete=models.CASCADE,
        related_name="maps",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.name} - {self.tag}>"


class MapPool(models.Model):
    id = PrefixIDField(primary_key=True, prefix="map_pool")
    name = models.CharField(max_length=255, unique=True)
    maps = models.ManyToManyField(Map, related_name="map_pools")
    guild = models.ForeignKey(
        "guilds.Guild",
        on_delete=models.CASCADE,
        related_name="map_pools",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if not self.guild else f"<{self.name} - {self.guild.name}>"


class MapBan(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="map_bans")
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="map_bans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.team.name} - {self.map.name}>"


class MapPick(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="map_selected"
    )
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="map_picks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.team.name} - {self.map.name}>"


class MatchConfig(models.Model):
    id = PrefixIDField(primary_key=True, prefix="match_config")
    name = models.CharField(max_length=255, unique=True)
    game_mode = models.CharField(
        max_length=255, choices=GameMode.choices, default=GameMode.COMPETITIVE
    )
    type = models.CharField(
        max_length=255, choices=MatchType.choices, default=MatchType.BO1
    )
    map_pool = models.ForeignKey(
        MapPool,
        on_delete=models.CASCADE,
        related_name="match_configs",
        null=True,
        blank=True,
    )
    map_sides = models.JSONField(null=True, blank=True)
    clinch_series = models.BooleanField(default=False)
    max_players = models.PositiveIntegerField(default=10)
    cvars = models.JSONField(null=True, blank=True)
    guild = models.ForeignKey(
        "guilds.Guild",
        on_delete=models.CASCADE,
        related_name="match_configs",
        null=True,
        blank=True,
    )
    shuffle_teams = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MatchManager(models.Manager):
    def check_server_is_available_for_match(self, server):
        return not self.filter(
            Q(server=server)
            & (Q(status=MatchStatus.LIVE) | Q(status=MatchStatus.STARTED))
        ).exists()


# Create your models here.
class Match(models.Model):
    objects = MatchManager()
    status = models.CharField(
        max_length=255, choices=MatchStatus.choices, default=MatchStatus.CREATED
    )
    config = models.ForeignKey(
        MatchConfig,
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    team1 = models.ForeignKey(
        "players.Team",
        on_delete=models.CASCADE,
        related_name="matches_team1",
        null=True,
        blank=True,
    )
    team2 = models.ForeignKey(
        "players.Team",
        on_delete=models.CASCADE,
        related_name="matches_team2",
        null=True,
        blank=True,
    )
    winner_team = models.ForeignKey(
        "players.Team",
        on_delete=models.CASCADE,
        related_name="matches_winner",
        null=True,
        blank=True,
    )
    map_bans = models.ManyToManyField(
        MapBan, related_name="matches_map_bans", blank=True
    )
    map_picks = models.ManyToManyField(
        MapPick, related_name="matches_map_picks", blank=True
    )
    last_map_ban = models.ForeignKey(
        MapBan,
        on_delete=models.SET_NULL,
        related_name="matches_last_map_ban",
        null=True,
        blank=True,
    )
    last_map_pick = models.ForeignKey(
        MapPick,
        on_delete=models.SET_NULL,
        related_name="matches_last_map_pick",
        null=True,
        blank=True,
    )
    maplist = models.JSONField(null=True, blank=True)
    cvars = models.JSONField(null=True, blank=True)
    message_id = models.CharField(max_length=255, null=True, blank=True)
    author = models.ForeignKey(
        "players.DiscordUser",
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
    )
    server = models.ForeignKey(
        "servers.Server",
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    guild = models.ForeignKey(
        "guilds.Guild",
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    embed = models.ForeignKey(
        "guilds.Embed",
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.status} - {self.config.name} - {self.pk}>"

    @property
    def api_key_header(self):
        return "Authorization"

    @property
    def load_match_command_name(self):
        return "matchzy_loadmatch_url"

    def get_team1_players_dict(self):
        return {
            "name": self.team1.name,
            "players": self.team1.get_players_dict(),
        }

    def get_team2_players_dict(self):
        return {
            "name": self.team2.name,
            "players": self.team2.get_players_dict(),
        }

    def get_matchzy_config(self):
        num_maps = 1 if self.config.type == MatchType.BO1 else 3
        players_count = self.team1.players.count() + self.team2.players.count()
        players_per_team = players_count / 2
        players_per_team_rounded = math.ceil(players_per_team)
        matchzy_config = {
            "matchid": self.pk,
            "team1": self.get_team1_players_dict(),
            "team2": self.get_team2_players_dict(),
            "num_maps": num_maps,
            "maplist": self.maplist,
            "map_sides": self.config.map_sides,
            "clinch_series": self.config.clinch_series,
            "players_per_team": players_per_team_rounded,
        }
        if self.cvars:
            config_cvars = self.config.cvars
            if config_cvars:
                self.cvars.update(config_cvars)
            matchzy_config["cvars"] = self.cvars
        if self.config.game_mode == GameMode.WINGMAN:
            matchzy_config["wingman"] = True
        return matchzy_config

    def get_connect_command(self):
        return "" if not self.server else self.server.get_connect_string()

    def get_author_token(self):
        return UserModel.objects.get(player__discord_user=self.author).get_token()

    def create_webhook_cvars(self, webhook_url: str):
        self.cvars = self.cvars or {}
        self.cvars.update(
            {
                "matchzy_remote_log_url": webhook_url,
                "matchzy_remote_log_header_key": self.api_key_header,
                "matchzy_remote_log_header_value": f"Bearer {self.get_author_token()}",
            }
        )
        self.save()

    def ban_map(self, team: Team, map: Map):
        """
        Ban a map

        Args:
            team (Team): Team that bans the map
            map (Map): Map to ban
        """
        map_ban = MapBan.objects.create(team=team, map=map)
        self.map_bans.add(map_ban)
        self.last_map_ban = map_ban

        if self.config.type == MatchType.BO1:
            # 6 bans
            map_bans_count = self.map_bans.count()
            # 7 maps
            map_pool_count = self.config.map_pool.maps.count() - 1
            if map_bans_count == map_pool_count:
                # Select the last map
                map_to_select = (
                    self.config.map_pool.maps.exclude(
                        tag__in=self.map_bans.values_list("map__tag", flat=True)
                    )
                    .exclude(tag__in=self.map_picks.values_list("map__tag", flat=True))
                    .first()
                )
                self.maplist = [map_to_select.tag]
                self.status = MatchStatus.READY_TO_LOAD
        elif self.config.type == MatchType.BO3:
            map_pool_count = self.config.map_pool.maps.count()
            # 4 bans
            map_bans_count = self.map_bans.count()
            # 7 maps
            map_pool_count_minus_three = (
                map_pool_count - 3
            )  # minus 3 because we need to have 3 maps left
            if map_bans_count == map_pool_count_minus_three:
                map_to_select = (
                    self.config.map_pool.maps.exclude(
                        tag__in=self.map_bans.values_list("map__tag", flat=True)
                    )
                    .exclude(tag__in=self.map_picks.values_list("map__tag", flat=True))
                    .first()
                )
                self.maplist.append(map_to_select.tag)
                self.status = MatchStatus.READY_TO_LOAD

        self.save()
        return self

    def pick_map(self, team, map):
        map_pick = MapPick.objects.create(team=team, map=map)
        self.map_picks.add(map_pick)
        # add map to maplist without removing it
        self.maplist.append(map.tag)
        self.last_map_pick = map_pick
        self.save()
        return self

    def shuffle_players(self):
        players_list = list(self.team1.players.all()) + list(self.team2.players.all())
        players_count = len(players_list)
        middle_index = players_count // 2
        team1_players = players_list[:middle_index]
        team2_players = players_list[middle_index:]
        self.team1.players.set(team1_players)
        self.team1.leader = team1_players[0]
        self.team2.players.set(team2_players)
        self.team2.leader = team2_players[0]
        self.save()

    def change_teams_name(self):
        self.team1.name = f"team_{self.team1.leader.steam_user.username}"
        self.team1.save()
        self.team2.name = f"team_{self.team2.leader.steam_user.username}"
        self.team2.save()

    def add_player_to_match(self, player, team: str = None):
        if team:
            if team == "team1":
                if self.team2.players.filter(id=player.id).exists():
                    self.team2.players.remove(player)
                self.team1.players.add(player)
            elif team == "team2":
                if self.team1.players.filter(id=player.id).exists():
                    self.team1.players.remove(player)
                self.team2.players.add(player)
        else:
            if self.team1.players.count() < self.team2.players.count():
                self.team1.players.add(player)
                self.embed.fields.get(name="Team 1").value = f"""
                        ```
                        Name: {self.team1.name}
                        Captain: {self.team1.leader.player.discord_user.username if self.team1.leader else "No captain"}
                        ```
                        ```
                        {[player.discord_user.username for player in self.team1.players.all() if self.team1.players.count() > 0]}
                        ```
                        """
            elif self.team2.players.count() < self.team1.players.count():
                self.team2.players.add(player)
                self.embed.fields.get(name="Team 2").value = f"""
                                    ```
                                    Name: {self.team2.name}
                                    Captain: {self.team2.leader.player.discord_user.username if self.team2.leader else "No captain"}
                                    ```
                                    ```
                                    {[player.discord_user.username for player in self.team2.players.all() if self.team2.players.count() > 0]}
                                    ```
                                    """
            else:
                self.team1.players.add(player)
        self.embed.save()
        self.save()

        return self

    def remove_player_from_match(self, player):
        if player in self.team1.players.all():
            self.team1.players.remove(player)
        elif player in self.team2.players.all():
            self.team2.players.remove(player)
        self.save()
        return self

    def start_match(self):
        if self.config.shuffle_teams:
            self.shuffle_players()
            self.change_teams_name()
            self.status = MatchStatus.MAP_VETO
        else:
            self.status = MatchStatus.CAPTAINS_SELECT

        self.save()
        return self

    def set_team_captain(self, player, team):
        if team == "team1":
            print("Setting team1 captain")
            self.team1.leader = player
            self.team1.save()
        elif team == "team2":
            print("Setting team2 captain")
            self.team2.leader = player
            self.team2.save()
        if self.team1.leader and self.team2.leader:
            self.status = MatchStatus.MAP_VETO
            self.change_teams_name()
        self.save()
        return self

    def get_team_by_player(self, player):
        if player in self.team1.players.all():
            return self.team1
        elif player in self.team2.players.all():
            return self.team2
        return None

    def get_maps_left(self):
        maps_left = self.config.map_pool.maps.exclude(
            tag__in=self.map_bans.values_list("map__tag", flat=True)
        ).exclude(tag__in=self.map_picks.values_list("map__tag", flat=True))
        if self.config.type == MatchType.BO1 and len(maps_left) == 1:
            return []
        return [map.tag for map in maps_left]

    def get_next_ban_team(self):
        return self.team1 if self.last_map_ban.team == self.team2 else self.team2


@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    if created:
        team1_player = Player.objects.get(discord_user=instance.author)
        team1 = Team.objects.create(name="Team 1")
        team1.players.add(team1_player)
        team1.save()
        team2 = Team.objects.create(name="Team 2")

        instance.team1 = team1
        instance.team2 = team2

        print(f"Created {team1}")
        print(f"Created {team2}")

        # create embed
        embed = Embed.objects.create(
            title=f"Match {instance.pk} - {instance.config.name}",
            description=f"""
            ```
            Config: {instance.config.name}
            Type: {instance.config.type}
            Status: {instance.status}
            Game mode: {instance.config.game_mode}
            Map Pool: {instance.config.map_pool.name if instance.config.map_pool else "No map pool"}
            Max Players: {instance.config.max_players}
            Map Sides: {instance.config.map_sides}
            Clinch Series: {instance.config.clinch_series}
            Custom cvars: {instance.config.cvars if instance.config.cvars else "No custom cvars"}
            ```
            """,
            author=instance.author.username,
            footer=f"{instance.pk} {instance.created_at}",
        )
        team1_players = [player.discord_user.username for player in team1.players.all()]
        team2_players = [player.discord_user.username for player in team2.players.all()]
        team1_players_str = "\n".join(team1_players)
        team2_players_str = "\n".join(team2_players)

        fields = [
            EmbedField.objects.create(
                order=1,
                name="Team 1",
                value=f"""
                ```
                Name: {instance.team1.name}
                Captain: {instance.team1.leader.discord_user.username if instance.team1.leader else "No captain"}
                ```
                ```
                {team1_players_str}
                ```
                """,
                inline=True,
            ),
            EmbedField.objects.create(
                order=2,
                name="Team 2",
                value=f"""
                ```
                Name: {instance.team2.name}
                Captain: {instance.team2.leader.discord_user.username if instance.team2.leader else "No captain"}
                ```
                ```
                {team2_players_str}
                ```
                """,
                inline=True,
            ),
        ]
        embed.fields.set(fields)
        instance.embed = embed
        instance.save()
    else:
        print("Match updated")
        print(f"Team 1 {instance.team1.players.count()}")
        print(f"Team 2 {instance.team2.players.count()}")
        instance.embed.title = f"Match {instance.pk}"
        instance.embed.description = f"""
            ```
            Config: {instance.config.name}
            Type: {instance.config.type}
            Status: {instance.status}
            Game mode: {instance.config.game_mode}
            Map Pool: {instance.config.map_pool.name if instance.config.map_pool else "No map pool"}
            Max Players: {instance.config.max_players}
            Map Sides: {instance.config.map_sides}
            Clinch Series: {instance.config.clinch_series}
            Custom cvars: {instance.config.cvars if instance.config.cvars else "No custom cvars"}
            ```
            """

        team1_players = [
            player.discord_user.username for player in instance.team1.players.all()
        ]
        team2_players = [
            player.discord_user.username for player in instance.team2.players.all()
        ]
        team1_players_str = "\n".join(team1_players)
        team2_players_str = "\n".join(team2_players)

        team1_field = instance.embed.fields.get(name="Team 1")
        team1_field.value = f"""
        ```
        Name: {instance.team1.name}
        Captain: {instance.team1.leader.discord_user.username if instance.team1.leader else "No captain"}
        ```
        ```
        {team1_players_str}
        ```
        """
        team1_field.save()
        team2_field = instance.embed.fields.get(name="Team 2")
        team2_field.value = f"""
        ```
        Name: {instance.team2.name}
        Captain: {instance.team2.leader.discord_user.username if instance.team2.leader else "No captain"}
        ```
        ```
        {team2_players_str}
        ```
        """
        team2_field.save()
        if instance.status == MatchStatus.READY_TO_LOAD:
            if instance.server:
                server_detail_field = EmbedField.objects.create(
                    order=instance.embed.fields.last().order + 1,
                    name="Server details",
                    value=f"```{instance.get_connect_command()}```",
                )
                instance.embed.fields.add(server_detail_field)
        instance.embed.save()
