# Generated by Django 5.0.6 on 2024-05-09 20:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("guilds", "0004_remove_guild_members"),
        ("matches", "0021_map_guild_alter_map_name_alter_map_tag"),
        ("players", "0005_alter_player_steam_user"),
        ("servers", "0006_remove_server_max_players"),
    ]

    operations = [
        migrations.AlterField(
            model_name="map",
            name="guild",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="maps",
                to="guilds.guild",
            ),
        ),
        migrations.AlterField(
            model_name="mappool",
            name="guild",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="map_pools",
                to="guilds.guild",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="players.discorduser",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="matches.matchconfig",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="cvars",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="match",
            name="guild",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="guilds.guild",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="last_map_ban",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_last_map_ban",
                to="matches.mapban",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="last_map_pick",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_last_map_pick",
                to="matches.mappick",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="map_pool",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="matches.mappool",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="maplist",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="match",
            name="message_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="match",
            name="server",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches",
                to="servers.server",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="status",
            field=models.CharField(
                choices=[
                    ("CREATED", "Created"),
                    ("STARTED", "Started"),
                    ("LIVE", "Live"),
                    ("FINISHED", "Finished"),
                    ("CANCELLED", "Cancelled"),
                ],
                default="CREATED",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="team1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_team1",
                to="players.team",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="team2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_team2",
                to="players.team",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="winner_team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_winner",
                to="players.team",
            ),
        ),
        migrations.AlterField(
            model_name="matchconfig",
            name="guild",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="match_configs",
                to="guilds.guild",
            ),
        ),
    ]
