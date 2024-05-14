# Generated by Django 5.0.4 on 2024-04-09 18:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("guilds", "0002_guild_lobby_channel_guild_team1_channel_and_more"),
        ("players", "0004_alter_team_leader"),
    ]

    operations = [
        migrations.AddField(
            model_name="guild",
            name="members",
            field=models.ManyToManyField(
                related_name="guild_members", to="players.discorduser"
            ),
        ),
    ]
