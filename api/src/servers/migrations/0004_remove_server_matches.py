# Generated by Django 5.0.4 on 2024-04-04 14:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("servers", "0003_server_guild_server_is_public_server_password"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="server",
            name="matches",
        ),
    ]
