import pytest
from django.contrib.auth import get_user_model
from guilds.models import Guild

User = get_user_model()


@pytest.mark.django_db
def test_create_guild(user):
    guild = Guild.objects.create(
        name="test_guild",
        guild_id="123456",
        owner=user,
        lobby_channel="123456",
        team1_channel="123456",
        team2_channel="123456",
    )

    assert guild.name == "test_guild"
    assert guild.guild_id == "123456"
    assert guild.owner == user
    assert guild.lobby_channel == "123456"
    assert guild.team1_channel == "123456"
    assert guild.team2_channel == "123456"
    assert guild.embed.title == f"Guild configuration {guild.name}"
    assert guild.embed.author == user.username
    assert guild.embed.fields.get(name="Lobby Channel").value == "@<123456>"
    assert guild.embed.fields.get(name="Team 1 Channel").value == "@<123456>"
    assert guild.embed.fields.get(name="Team 2 Channel").value == "@<123456>"


@pytest.mark.django_db
def test_is_created_embed_on_guild_create(guild):
    assert guild.embed is not None
    assert guild.embed.title == f"Guild configuration {guild.name}"
    assert guild.embed.author == guild.owner.username
    assert guild.embed.fields.get(name="Lobby Channel").value == f"@<{guild.lobby_channel}>"
    assert guild.embed.fields.get(name="Team 1 Channel").value == f"@<{guild.team1_channel}>"
    assert guild.embed.fields.get(name="Team 2 Channel").value == f"@<{guild.team2_channel}>"


@pytest.mark.django_db
def test_create_config_embed(guild):
    embed = guild.create_config_embed()
    assert embed.title == f"Guild configuration {guild.name}"
    assert embed.author == guild.owner.username
    assert embed.fields.get(name="Lobby Channel").value == f"@<{guild.lobby_channel}>"
    assert embed.fields.get(name="Team 1 Channel").value == f"@<{guild.team1_channel}>"
    assert embed.fields.get(name="Team 2 Channel").value == f"@<{guild.team2_channel}>"
    assert guild.embed == embed