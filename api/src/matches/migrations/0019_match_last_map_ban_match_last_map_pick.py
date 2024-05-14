# Generated by Django 5.0.4 on 2024-04-20 14:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("matches", "0018_match_guild"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="last_map_ban",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_last_map_ban",
                to="matches.mapban",
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="last_map_pick",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="matches_last_map_pick",
                to="matches.mappick",
            ),
        ),
    ]