# Generated by Django 5.0.6 on 2024-05-09 21:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("matches", "0023_alter_mappick_map_alter_match_author_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="match",
            name="map_pool",
        ),
        migrations.AddField(
            model_name="matchconfig",
            name="map_pool",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="match_configs",
                to="matches.mappool",
            ),
        ),
    ]
