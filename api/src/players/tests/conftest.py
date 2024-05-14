import pytest

from players.models import DiscordUser, SteamUser, Player, Team


@pytest.fixture
def discord_user_data():
    return {
        "user_id": "1133332759834787860",
        "username": "qwizi2",
    }


@pytest.fixture
def steam_user_data():
    return {
        "username": "Qwizi",
        "steamid64": "76561198190469450",
        "steamid32": "STEAM_1:0:115101861",
        "profile_url": "https://steamcommunity.com/id/34534645645/",
        "avatar": "https://avatars.steamstatic.com/d95f7e69a5cfb9c09acf1ecb6a2106239297f668_full.jpg",
    }


@pytest.fixture
def player(discord_user_data, steam_user_data):
    discord_user = DiscordUser.objects.create(**discord_user_data)
    steam_user = SteamUser.objects.create(**steam_user_data)
    return Player.objects.create(discord_user=discord_user, steam_user=steam_user)


@pytest.fixture
def players(player):
    players_dict = [
        {
            "discord_user": {
                "user_id": "493797036869681153",
                "username": ".rzeznia",
            },
            "steam_user": {
                "username": "Abdull Mohamed Mother Fakier",
                "steamid64": "76561198151042669",
                "steamid32": "STEAM_1:1:95388470",
                "profile_url": "https://steamcommunity.com/profiles/76561198151042669/",
                "avatar": "https://avatars.steamstatic.com/40b0b3e018e6267f53e549afc7a7d58777f0541c_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "808695534872297505",
                "username": "starss",
            },
            "steam_user": {
                "username": "ST4RSS",
                "steamid64": "76561199128194020",
                "steamid32": "asdasda",
                "profile_url": "https://steamcommunity.com/profiles/76561199128194020/",
                "avatar": "https://avatars.cloudflare.steamstatic.com/6cc7f1faa69366ae290dd965f6f4a0c18241a15e_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "567650749090234368",
                "username": "harvi9",
            },
            "steam_user": {
                "username": "HarVi",
                "steamid64": "76561198234988840",
                "steamid32": "STEAM_1:0:137361556",
                "profile_url": "https://steamcommunity.com/id/HarViPLgurom/",
                "avatar": "https://avatars.steamstatic.com/adc102a7a0b4ff30c881c149a4a572b118dfb806_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "859429903170273321",
                "username": "olis1337",
            },
            "steam_user": {
                "username": "Olis",
                "steamid64": "76561198984922371",
                "steamid32": "STEAM_1:1:512328321",
                "profile_url": "https://steamcommunity.com/profiles/76561198984922371/",
                "avatar": "https://avatars.steamstatic.com/6abdf949d7ae65b03fae58edab2970dff2d2238c_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "907005053141909594",
                "username": "virdis__",
            },
            "steam_user": {
                "username": "Virdis",
                "steamid64": "76561198156230787",
                "steamid32": "STEAM_1:1:97982529",
                "profile_url": "https://steamcommunity.com/id/jiarhbdjiaefkw/",
                "avatar": "https://avatars.steamstatic.com/821b29b66cf0d45d6c8fdd357d5315f9ee1d3e6a_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "495214448361996298",
                "username": "striker6414",
            },
            "steam_user": {
                "username": "☁ストライカー☁",
                "steamid64": "76561198871920745",
                "steamid32": "STEAM_1:1:455827508",
                "profile_url": "https://steamcommunity.com/profiles/76561198871920745/",
                "avatar": "https://avatars.steamstatic.com/543bb32f9249e6738288c0d3ac6987ee25983c41_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "315418005913993216",
                "username": "qwewt",
            },
            "steam_user": {
                "username": "qwewt",
                "steamid64": "76561198121971215",
                "steamid32": "STEAM_1:1:80852743",
                "profile_url": "https://steamcommunity.com/id/qwewt/",
                "avatar": "https://avatars.steamstatic.com/f0501a13e211c2b9f8c6f8e3ee3a3b2db4d9938c_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "451080461448511498",
                "username": "_0lcha",
            },
            "steam_user": {
                "username": "0lchaツ",
                "steamid64": "76561198843434579",
                "steamid32": "STEAM_1:1:441584425",
                "profile_url": "https://steamcommunity.com/profiles/76561198843434579/",
                "avatar": "https://avatars.steamstatic.com/ee71a010283e7665fb23a78f22ad4a990e865067_full.jpg",
            },
        },
        {
            "discord_user": {
                "user_id": "463451929343688727",
                "username": "zajonc.",
            },
            "steam_user": {
                "username": "♣ kashana",
                "steamid64": "76561199105283370",
                "steamid32": "STEAM_1:0:572508821",
                "profile_url": "https://steamcommunity.com/id/zajoncaccount/",
                "avatar": "https://avatars.steamstatic.com/ad165f4ac66f77bdd759fda4d5e32c8d8925ba25_full.jpg",
            },
        },
    ]
    players = [player]

    for player_dict in players_dict:
        dc_user = DiscordUser.objects.create(**player_dict["discord_user"])
        steam_user = SteamUser.objects.create(**player_dict["steam_user"])
        player = Player.objects.create(discord_user=dc_user, steam_user=steam_user)
        players.append(player)
    return players


@pytest.fixture
def teams() -> tuple[Team, Team]:
    return Team.objects.create(name="Team 1"), Team.objects.create(name="Team 2")


@pytest.fixture
def teams_with_players(teams, players):
    team1, team2 = teams
    team1.players.add(*players[:5])
    team1.leader = players[0]
    team1.save()
    team2.players.add(*players[5:])
    team2.leader = players[5]
    team2.save()
    print(team1.players.count())
    print(team2.players.count())
    return team1, team2


@pytest.fixture
def default_author(admin_user, player):
    admin_user.username = player.discord_user.username
    admin_user.player = player
    admin_user.save()
    return admin_user
