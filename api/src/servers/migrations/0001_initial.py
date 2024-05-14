# Generated by Django 5.0.2 on 2024-02-21 15:07

import prefix_id.field
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("matches", "0002_remove_match_map_remove_match_players_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Server",
            fields=[
                (
                    "id",
                    prefix_id.field.PrefixIDField(
                        editable=False,
                        max_length=29,
                        prefix="server",
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("ip", models.CharField(max_length=100)),
                ("name", models.CharField(max_length=100)),
                ("port", models.PositiveIntegerField()),
                ("rcon_password", models.CharField(max_length=100)),
                ("max_players", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "matches",
                    models.ManyToManyField(related_name="servers", to="matches.match"),
                ),
            ],
        ),
    ]
