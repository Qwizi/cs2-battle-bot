# Generated by Django 5.0.6 on 2024-05-09 20:18

import django.db.models.deletion
import prefix_id.field
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("guilds", "0004_remove_guild_members"),
        ("matches", "0019_match_last_map_ban_match_last_map_pick"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="match",
            name="clinch_series",
        ),
        migrations.RemoveField(
            model_name="match",
            name="map_sides",
        ),
        migrations.RemoveField(
            model_name="match",
            name="maps",
        ),
        migrations.RemoveField(
            model_name="match",
            name="num_maps",
        ),
        migrations.RemoveField(
            model_name="match",
            name="players_per_team",
        ),
        migrations.RemoveField(
            model_name="match",
            name="type",
        ),
        migrations.CreateModel(
            name="MapPool",
            fields=[
                (
                    "id",
                    prefix_id.field.PrefixIDField(
                        editable=False,
                        max_length=31,
                        prefix="map_pool",
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "guild",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="map_pools",
                        to="guilds.guild",
                    ),
                ),
                (
                    "maps",
                    models.ManyToManyField(related_name="map_pools", to="matches.map"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="match",
            name="map_pool",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="matches.mappool",
            ),
        ),
        migrations.CreateModel(
            name="MatchConfig",
            fields=[
                (
                    "id",
                    prefix_id.field.PrefixIDField(
                        editable=False,
                        max_length=35,
                        prefix="match_config",
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "game_mode",
                    models.CharField(
                        choices=[
                            ("COMPETITIVE", "Competitive"),
                            ("WINGMAN", "Wingman"),
                            ("AIM", "Aim"),
                        ],
                        default="COMPETITIVE",
                        max_length=255,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("BO1", "Bo1"), ("BO3", "Bo3"), ("BO5", "Bo5")],
                        default="BO1",
                        max_length=255,
                    ),
                ),
                ("map_sides", models.JSONField(null=True)),
                ("clinch_series", models.BooleanField(default=False)),
                ("max_players", models.PositiveIntegerField(default=10)),
                ("cvars", models.JSONField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "guild",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_configs",
                        to="guilds.guild",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="match",
            name="config",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="matches.matchconfig",
            ),
        ),
    ]