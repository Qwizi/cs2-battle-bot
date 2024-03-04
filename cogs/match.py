import json
import os
import discord
from discord.ui import View

from discord.ext import commands, tasks
from dotenv import load_dotenv
import httpx

load_dotenv()

TESTING = os.environ.get("TESTING", False)


from utils import (
    ban_map,
    create_match,
    get_connect_account_link,
    get_curent_match,
    get_match,
    get_teams_autocomplete,
    load_match,
    pick_map,
    recreate_match,
    shuffle_teams,
)

guild_id = 639034263999741953
info_channel_id = 1210935599972749312
status_message_id = 1213212463563280454
general_channel_id = 1211078909127561257
lobby_channel_id = 1211059521762492486
team1_channel_id = 1211059841993281537
team2_channel_id = 1211059895202484344


class MapView(View):
    def __init__(self):
        super().__init__()


class MatchView(View):
    pass


class MatchCog(commands.Cog):
    def __init__(self, bot, pubsub):
        self.bot: discord.Bot = bot
        self.pubsub = pubsub
        self.listen_events.start()

    match = discord.SlashCommandGroup(
        name="match", description="Commands for managing matches"
    )

    async def get_match_in_map_interaction(self, interaction: discord.Interaction):
        current_match_data, current_match_response = await get_curent_match()
        if current_match_response.status_code != 200:
            print("No current match")
            await interaction.followup.send("No current match", ephemeral=True)
            return
        match_id = current_match_data.get("matchid")
        print(match_id)
        match, match_response = await get_match(match_id)
        if match_response.status_code != 200:
            print("No match")
            await interaction.followup.send("No match", ephemeral=True)
            return match, match_response
        return match

    def get_discord_users_ids(self, players):
        return [int(player.get("discord_user").get("user_id")) for player in players]

    def get_teams_discord_users_ids(self, team1, team2):
        team1_discord_users_ids = self.get_discord_users_ids(team1.get("players"))
        team2_discord_users_ids = self.get_discord_users_ids(team2.get("players"))
        return team1_discord_users_ids, team2_discord_users_ids

    def check_user_is_in_team(self, user, team1, team2):
        (
            team1_discord_users_ids,
            team2_discord_users_ids,
        ) = self.get_teams_discord_users_ids(team1, team2)
        if (
            user.id not in team1_discord_users_ids
            and user.id not in team2_discord_users_ids
        ):
            return False
        return True

    def get_team_leader(self, team):
        return int(team.get("players")[0].get("discord_user").get("user_id"))

    def get_team_leader_name(self, team):
        return team.get("players")[0].get("discord_user").get("username")

    def get_team_leaders(self, team1, team2):
        team1_leader = self.get_team_leader(team1)
        team2_leader = self.get_team_leader(team2)
        return team1_leader, team2_leader

    def check_is_user_leader(self, user, team1, team2):
        team1_leader, team2_leader = self.get_team_leaders(team1, team2)
        if user.id != team1_leader and user.id != team2_leader:
            return False
        return True

    def check_is_user_can_pick(self, user, map_picks):
        if len(map_picks) == 0:
            return True
        last_map_pick = map_picks[-1]
        last_pick_team = last_map_pick.get("team")
        last_pick_team_leader = self.get_team_leader(last_pick_team)
        if not TESTING and user.id == last_pick_team_leader:
            return False
        return True

    async def start_match_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                "Tylko autor komendy moze wykonac ta akcje", ephemeral=True
            )
            return
        try:
            response = await load_match()
        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        else:
            await interaction.followup.send("Pomyślnie załadowano mecz!")

    async def recreate_match_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                "Tylko autor komendy moze wykonac ta akcje", ephemeral=True
            )
            return
        try:
            current_match, current_match_response = await get_curent_match()
            match_id = current_match.get("matchid")
            match, match_response = await recreate_match(match_id)
            print(match)
            match_type = match.get("type")
            map_select_view, select_menu = self.create_map_select_view(
                "Wybierz mape do zbanowania",
                [
                    discord.SelectOption(label=map["tag"], value=map["tag"])
                    for map in match.get("maps")
                ],
            )
            match match_type:
                case "BO1":
                    select_menu.callback = self.bo1_map_ban_callback
                case "BO3":
                    select_menu.callback = self.bo3_map_ban_callback

            await interaction.edit(view=map_select_view)

        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )

    async def shuffle_teams_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # check if interaction user is a author of command
        if interaction.user.id != int(interaction.message.embeds[0].footer.text):
            await interaction.followup.send(
                "Tylko autor komendy moze przelosowac druzyny", ephemeral=True
            )
            return
        try:
            current_match, current_match_response = await get_curent_match()
            match_id = current_match.get("matchid")
            match, match_response = await shuffle_teams(match_id)
            create_match_embed = self.create_match_embed(
                match, int(interaction.message.embeds[0].footer.text)
            )
            await interaction.edit(embed=create_match_embed)

        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )

    async def bo1_map_ban_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        message = await interaction.channel.fetch_message(interaction.message.id)
        chosen_map = interaction.data["values"][0]
        try:
            match = await self.get_match_in_map_interaction(interaction)
            match_id = match.get("id")
            team1 = match.get("team1")
            team2 = match.get("team2")

            if not self.check_user_is_in_team(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes w zadnym teamie", ephemeral=True
                )
                return

            team1_leader, team2_leader = self.get_team_leaders(team1, team2)

            if not self.check_is_user_leader(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes liderem w zadnym teamie", ephemeral=True
                )
                return
            map_bans = match.get("map_bans")
            if not self.check_is_user_can_pick(interaction.user, map_bans):
                await interaction.followup.send(
                    "Teraz banuje druzyna przeciwna", ephemeral=True
                )
                return
            team_id = None
            if interaction.user.id == team1_leader:
                team_id = team1.get("id")
            else:
                team_id = team2.get("id")
            ban_map_data, ban_map_response = await ban_map(
                match_id, team_id, chosen_map
            )

            match, match_response = await get_match(match_id)
            print(match)

            view = MapView()
            ban_team_leader_name = (
                self.get_team_leader_name(team2)
                if team1_leader == interaction.user.id
                else self.get_team_leader_name(team1)
            )
            placeholder = f"Teraz Banuje {ban_team_leader_name}"
            select_menu = discord.ui.Select(
                placeholder=placeholder,
                options=[
                    discord.SelectOption(label=map["tag"], value=map["tag"])
                    for map in match.get("maps")
                ],
            )
            view.add_item(select_menu)
            select_menu.callback = self.bo1_map_ban_callback
            await message.edit(view=view)
            if len(match.get("maps")) == 1:
                match_launch_embed = self.create_launch_match_embed(
                    message.embeds[0],
                    match,
                    int(interaction.message.embeds[0].footer.text),
                )
                match_launch_view = self.create_launch_match_view()
                await interaction.followup.send(
                    f"Gramy mape {match.get('maps')[0].get('tag')}"
                )
                await message.edit(view=match_launch_view, embed=match_launch_embed)
            else:
                await interaction.followup.send(
                    f"<@{interaction.user.id}> zbanowal mape {chosen_map}"
                )
        except httpx.HTTPStatusError as e:
            print(e.response.json())
            await interaction.followup.send("Failed to ban map", ephemeral=True)
        except httpx.HTTPError as e:
            print(e)
            await interaction.followup.send("Failed to ban map", ephemeral=True)

    async def bo3_map_pick_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        message = await interaction.channel.fetch_message(interaction.message.id)
        chosen_map = interaction.data["values"][0]
        try:
            match = await self.get_match_in_map_interaction(interaction)
            match_id = match.get("id")
            team1 = match.get("team1")
            team2 = match.get("team2")

            if not self.check_user_is_in_team(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes w zadnym teamie", ephemeral=True
                )
                return

            team1_leader, team2_leader = self.get_team_leaders(team1, team2)

            if not self.check_is_user_leader(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes liderem w zadnym teamie", ephemeral=True
                )
                return

            map_picks = match.get("map_picks")
            if not self.check_is_user_can_pick(interaction.user, map_picks):
                await interaction.followup.send(
                    "Teraz wybiera druzyna przeciwna", ephemeral=True
                )
                return

            team_id = None
            if interaction.user.id == team1_leader:
                team_id = team1.get("id")
            else:
                team_id = team2.get("id")
            pick_map_data, pick_map_response = await pick_map(
                match_id, team_id, chosen_map
            )

            match, match_response = await get_match(match_id)
            map_picks = match.get("map_picks")
            map_picks_tags = [map["map"]["tag"] for map in map_picks]
            maps_to_pick = [
                map["tag"]
                for map in match.get("maps")
                if map["tag"] not in map_picks_tags
            ]
            if len(map_picks) == 2:
                ban_team_leader_name = (
                    self.get_team_leader_name(team2)
                    if team1_leader == interaction.user.id
                    else self.get_team_leader_name(team1)
                )
                map_select_view, select_menu = self.create_map_select_view(
                    f"Teraz Banuje {ban_team_leader_name}",
                    [
                        discord.SelectOption(label=map, value=map)
                        for map in maps_to_pick
                    ],
                )
                select_menu.callback = self.bo3_map_ban_callback
                await message.edit(view=map_select_view)
            else:
                map_select_view, select_menu = self.create_map_select_view(
                    "Wybierz mape do wyboru",
                    options=[
                        discord.SelectOption(label=tag, value=tag)
                        for tag in maps_to_pick
                    ],
                )
                select_menu.callback = self.bo3_map_pick_callback
                await message.edit(view=map_select_view)
            await interaction.followup.send(
                f"<@{interaction.user.id}> wybral mape {chosen_map}"
            )
        except httpx.HTTPError as e:
            print(e)
            await interaction.followup.send("Failed to pick map", ephemeral=True)

    async def bo3_map_ban_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        message = await interaction.channel.fetch_message(interaction.message.id)
        chosen_map = interaction.data["values"][0]
        try:
            match = await self.get_match_in_map_interaction(interaction)
            match_id = match.get("id")
            team1 = match.get("team1")
            team2 = match.get("team2")

            if not self.check_user_is_in_team(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes w zadnym teamie", ephemeral=True
                )
                return

            team1_leader, team2_leader = self.get_team_leaders(team1, team2)

            if not self.check_is_user_leader(interaction.user, team1, team2):
                await interaction.followup.send(
                    "Nie jestes liderem w zadnym teamie", ephemeral=True
                )
                return

            map_bans = match.get("map_bans")
            if not self.check_is_user_can_pick(interaction.user, map_bans):
                await interaction.followup.send(
                    "Teraz banuje druzyna przeciwna", ephemeral=True
                )
                return
                # Jezeli teamy zbanowaly 2 mapy

            team_id = None
            if interaction.user.id == team1_leader:
                team_id = team1.get("id")
            else:
                team_id = team2.get("id")
            ban_map_data, ban_map_response = await ban_map(
                match_id, team_id, chosen_map
            )

            match, match_response = await get_match(match_id)
            map_bans = match.get("map_bans")
            if len(map_bans) == 2 or len(map_bans) == 3 or len(map_bans) == 4:
                print(f"Liczba banów {len(map_bans)}")
                match, match_response = await get_match(match_id)
                map_picks = match.get("map_picks")
                print(f"Liczba picków {len(map_picks)}")

                if len(map_picks) == 2:
                    map_picks_tags = [map["map"]["tag"] for map in map_picks]
                    maps_to_ban = [
                        map["tag"]
                        for map in match.get("maps")
                        if map["tag"] not in map_picks_tags
                    ]

                    ban_team_leader_name = (
                        self.get_team_leader_name(team2)
                        if team1_leader == interaction.user.id
                        else self.get_team_leader_name(team1)
                    )

                    map_select_view, select_menu = self.create_map_select_view(
                        f"Teraz Banuje {ban_team_leader_name}",
                        [
                            discord.SelectOption(label=map, value=map)
                            for map in maps_to_ban
                        ],
                    )
                    select_menu.callback = self.bo3_map_ban_callback
                    await message.edit(view=map_select_view)
                else:
                    map_select_view, select_menu = self.create_map_select_view(
                        "Wybierz mape do wyboru",
                        [
                            discord.SelectOption(label=map["tag"], value=map["tag"])
                            for map in match.get("maps")
                        ],
                    )
                    select_menu.callback = self.bo3_map_pick_callback
                    await message.edit(view=map_select_view)
            else:
                print("Liczba banów mniejsza niz 2")
                ban_team_leader_name = (
                    self.get_team_leader_name(team2)
                    if team1_leader == interaction.user.id
                    else self.get_team_leader_name(team1)
                )
                map_select_view, select_menu = self.create_map_select_view(
                    f"Teraz Banuje {ban_team_leader_name}",
                    [
                        discord.SelectOption(label=map["tag"], value=map["tag"])
                        for map in match.get("maps")
                    ],
                )
                select_menu.callback = self.bo3_map_ban_callback
                await message.edit(view=map_select_view)

            if len(match.get("maps")) == 3:
                launch_match_view = self.create_launch_match_view()
                match_launch_embed = self.create_launch_match_embed(
                    message.embeds[0],
                    match,
                    int(interaction.message.embeds[0].footer.text),
                )
                maps_tags = [f"{map['tag']}" for map in match.get("maps")]
                await interaction.followup.send(f"Gramy mapy {', '.join(maps_tags)}")
                await message.edit(view=launch_match_view, embed=match_launch_embed)
            else:
                await interaction.followup.send(
                    f"<@{interaction.user.id}> zbanowal mape {chosen_map}"
                )

        except httpx.HTTPError as e:
            print(e)
            await interaction.followup.send("Failed to ban map", ephemeral=True)

    @match.command(guild_ids=[guild_id])
    async def connect(self, ctx: discord.ApplicationContext):
        connect_account_link = get_connect_account_link()
        await ctx.respond(f"[Połącz konto]({connect_account_link})", ephemeral=True)

    @match.command(guild_ids=[guild_id])
    async def create(
        self,
        ctx: discord.ApplicationContext,
        shuffle_teams: discord.Option(bool, default=False, name="shuffle_teams"),
        match_type: discord.Option(
            str,
            choices=[
                discord.OptionChoice(name="BO1", value="BO1"),
                discord.OptionChoice(name="BO3", value="BO3"),
                discord.OptionChoice(name="BO5", value="BO5"),
            ],
            default="BO1",
            name="match_type",
        ),  # type: ignore
        # maplist: discord.Option(str, default="de_mirage,de_nuke"),  # type: ignore
        team1_id: discord.Option(
            str,
            autocomplete=discord.utils.basic_autocomplete(get_teams_autocomplete),
            required=False,
        ),  # type: ignore
        team2_id: discord.Option(
            str,
            autocomplete=discord.utils.basic_autocomplete(get_teams_autocomplete),
            required=False,
        ),  # type: ignore
    ):
        await ctx.defer()
        if ctx.author.voice is None:
            await ctx.followup.send("You're not in a voice channel.", ephemeral=True)
            return
        voice_channel = ctx.author.voice.channel
        members = voice_channel.members
        if not TESTING:
            if len(members) < 2:
                await ctx.followup.send(
                    "You need at least 2 players to create a match.", ephemeral=True
                )
                return
        try:
            discord_users_ids = (
                [ctx.author.id, 859429903170273321, 692055783650754650]
                if TESTING
                else [member.id for member in members]
            )
            # maplist = maplist.split(",")
            # print(maplist)
            api_token = os.environ.get("API_TOKEN")
            webhook_url = f"f{os.environ.get('API_URL')}/api/maches/webhook/"
            match_data = {
                "discord_users_ids": discord_users_ids,
                # "maplist": maplist,
                "shuffle_teams": shuffle_teams,
                "match_type": match_type,
                "cvars": {
                    "matchzy_remote_log_url": webhook_url,
                    "matchzy_remote_log_header_key": "X-Api-Key",
                    "matchzy_remote_log_header_value": api_token,
                },
            }
            created_match, created_match_response = await create_match(match_data)
            match_embed = self.create_match_embed(
                created_match, author_id=ctx.author.id
            )
            map_select_view, select_menu = self.create_map_select_view(
                "Wybierz mape do zbanowania",
                [
                    discord.SelectOption(label=map["tag"], value=map["tag"])
                    for map in created_match.get("maps")
                ],
            )
            shuffle_teams_button = discord.ui.Button(
                label="Przelosuj druzyny!",
                style=discord.ButtonStyle.secondary,
                emoji="🔀",
            )

            shuffle_teams_button.callback = self.shuffle_teams_button_callback
            map_select_view.add_item(shuffle_teams_button)
            match match_type:
                case "BO1":
                    select_menu.callback = self.bo1_map_ban_callback
                case "BO3":
                    select_menu.callback = self.bo3_map_ban_callback
            await ctx.followup.send(embed=match_embed, view=map_select_view)

        except httpx.HTTPStatusError as e:
            data = e.response.json()
            message = data.get("message")

            if message and "Discord user" in data.get("message"):
                user_id = data.get("user_id")
                await ctx.followup.send(
                    f"Uzytkownik <@{user_id}> nie jest zarejestrowany w bazie danych",
                )
            await ctx.followup.send(
                f"HTTPStatusError: Failed to create match {e}", ephemeral=True
            )
            print(data)
        except httpx.HTTPError as e:
            print(e)
            await ctx.followup.send("HTTPError: Failed to create match", ephemeral=True)
        except discord.errors.HTTPException as e:
            print(e)
            await ctx.followup.send(
                f"HTTPException: Failed to create match, {e}", ephemeral=True
            )
        except Exception as e:
            print(e)
            await ctx.followup.send(
                f"ApplicationCommandInvokeError: Failed to create match, {e}",
                ephemeral=True,
            )

    @tasks.loop(seconds=5)
    async def listen_events(self):
        message = self.pubsub.get_message()
        while message is not None:
            if message["type"] == "pmessage":
                data = message.get("data")
                if data is None:
                    return
                data = data.decode("utf-8")
                data = json.loads(data)
                event = data.get("event")
                if not event:
                    return
                match event:
                    case "going_live":
                        await self.on_going_live(data)
                    case "series_start":
                        await self.on_series_start(data)
                    case "series_end":
                        await self.on_series_end(data)
                    case "map_result":
                        await self.on_map_result(data)
                    case "round_end":
                        await self.on_round_end(data)
                    case "side_picked":
                        await self.on_side_picked(data)
                    case "map_picked":
                        await self.on_map_picked(data)
                    case "map_vetoed":
                        await self.on_map_vetoed(data)
            message = self.pubsub.get_message()

    @listen_events.before_loop
    async def before_listen_events(self):
        await self.bot.wait_until_ready()
        print("Starting listening events")

    @listen_events.after_loop
    async def after_listen_events(self):
        print("Stopped listening events")

    def get_players_mentioned_names(self, players):
        if not players:
            return []
        return [f"<@{player.get('discord_user').get('user_id')}>" for player in players]

    def create_match_embed(self, match, author_id: int) -> discord.Embed:
        team1 = match.get("team1")
        team2 = match.get("team2")
        team1_players = team1.get("players")
        team2_players = team2.get("players")
        team1_names = self.get_players_mentioned_names(team1_players)
        team2_names = self.get_players_mentioned_names(team2_players)

        team1_leader = int(team1_players[0].get("discord_user").get("user_id"))
        team2_leader = int(team2_players[0].get("discord_user").get("user_id"))

        team1_leader_mention = f"<@{team1_leader}>"
        team2_leader_mention = f"<@{team2_leader}>"

        maps = match.get("maps")
        maps_tags = [f"{map['tag']}" for map in maps]
        embed = discord.Embed(
            title="Mecz utworzony!",
            description="Mecz został utworzony.",
            color=discord.Colour.blurple(),  # Pycord provides a class with default colors you can choose from
        )
        embed.add_field(
            name=team1.get("name", "Team 1"),
            value=f"{', '.join(team1_names)}",
            inline=False,
        )
        embed.add_field(
            name="Lider",
            value=team1_leader_mention,
            inline=False,
        )
        embed.add_field(
            name=team2.get("name", "Team 2"),
            value=f"{', '.join(team2_names)}",
            inline=False,
        )
        embed.add_field(
            name="Lider",
            value=team2_leader_mention,
            inline=False,
        )
        embed.set_footer(text=author_id)
        return embed

    def create_launch_match_embed(
        self, old_embed: discord.Embed, match, author_id: int
    ):
        new_embed = discord.Embed()
        new_embed.color = old_embed.color
        new_embed.title = old_embed.title
        new_embed.description = old_embed.description
        new_embed.fields = old_embed.fields
        maps_tags = [f"{map['tag']}" for map in match.get("maps")]
        field_map_exists = False
        for field in old_embed.fields:
            if field.name == "Map":
                field_map_exists = True
                break
        if not field_map_exists:
            new_embed.add_field(
                name="Map",
                value=f"{', '.join(maps_tags)}",
                inline=False,
            )
        else:
            new_embed.set_field_at(
                4,
                name="Map",
                value=f"{', '.join(maps_tags)}",
                inline=False,
            )
        new_embed.set_footer(text=author_id)
        return new_embed

    def create_launch_match_view(self) -> discord.ui.View:
        match_view = MatchView()
        start_button = discord.ui.Button(
            label="Start!",
            style=discord.ButtonStyle.primary,
            emoji="🚀",
        )
        start_button.callback = self.start_match_button_callback
        join_button = discord.ui.Button(
            label="Dolacz do serwera!",
            style=discord.ButtonStyle.secondary,
            url="http://localhost:8002/accounts/join/",
        )
        recreate_button = discord.ui.Button(
            label="Utworz nowy mecz z tymi samymi druzynami!",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
        )
        recreate_button.callback = self.recreate_match_button_callback
        match_view.add_item(start_button)
        match_view.add_item(join_button)
        match_view.add_item(recreate_button)
        return match_view

    def create_map_select_view(
        self, placeholder: str, options: list[discord.SelectOption]
    ) -> tuple[discord.ui.View, discord.ui.Select]:
        view = MapView()
        select_menu = discord.ui.Select(
            placeholder="Wybierz mape do zbanowania"
            if not placeholder
            else placeholder,
            options=options,
        )
        view.add_item(select_menu)
        return view, select_menu

    async def on_going_live(self, data):
        print("Going live")

        try:
            current_match, current_match_response = await get_curent_match()
            if current_match_response.status_code != 200:
                print("No current match")
                return
            match_id = current_match.get("matchid")
            print(match_id)
            match, match_response = await get_match(match_id)
            if match_response.status_code != 200:
                print("No match")
                return
            print(match)
            team1 = match.get("team1")
            team2 = match.get("team2")
            guild = self.bot.get_guild(guild_id)
            general_channel = guild.get_channel(general_channel_id)
            lobby_channel = guild.get_channel(lobby_channel_id)
            team1_channel = guild.get_channel(team1_channel_id)
            team2_channel = guild.get_channel(team2_channel_id)

            for player in team1["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                try:
                    await user.move_to(team1_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

            for player in team2["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                if not user:
                    continue
                try:
                    await user.move_to(team2_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

        except httpx.HTTPError as e:
            print(e)

    async def on_series_start(self, data):
        try:
            print("Series start")
            print(data)
            guild = self.bot.get_guild(guild_id)
            general_channel = guild.get_channel(general_channel_id)
            lobby_channel = guild.get_channel(lobby_channel_id)
            team1_channel = guild.get_channel(team1_channel_id)
            team2_channel = guild.get_channel(team2_channel_id)
            current_match, current_match_response = await get_curent_match()
            if current_match_response.status_code != 200:
                print("No current match")
                return
            match_id = current_match.get("matchid")
            print(match_id)
            match, match_response = await get_match(match_id)
            if match_response.status_code != 200:
                print("No match")
                return
            print(match)
            team1 = match.get("team1")
            team2 = match.get("team2")

            for player in team1["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                try:
                    await user.move_to(lobby_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

            for player in team2["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                if not user:
                    continue
                try:
                    await user.move_to(lobby_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

            await team1_channel.edit(name=data["team1"]["name"])
            await team2_channel.edit(name=data["team2"]["name"])
            embed = discord.Embed(
                title="Konfiguracja meczu została załadowana!",
                description=f"{data['team1']['name']} vs {data['team2']['name']}",
                color=discord.Colour.blurple(),
            )
            await general_channel.send(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)

        except httpx.HTTPError as e:
            print(e)

    async def on_series_end(self, data):
        try:
            print("Series end")
            print(data)
            guild = self.bot.get_guild(guild_id)
            team1_channel = guild.get_channel(team1_channel_id)
            team2_channel = guild.get_channel(team2_channel_id)
            await team1_channel.edit(name="Team 1")
            await team2_channel.edit(name="Team 2")
        except discord.errors.HTTPException as e:
            print(e)

    async def on_map_result(self, data):
        print("Map result")
        try:
            current_match, current_match_response = await get_curent_match()
            if current_match_response.status_code != 200:
                print("No current match")
                return
            match_id = current_match.get("matchid")
            print(match_id)
            match, match_response = await get_match(match_id)
            if match_response.status_code != 200:
                print("No match")
                return
            print(match)
            team1 = match.get("team1")
            team2 = match.get("team2")
            guild = self.bot.get_guild(guild_id)
            general_channel = guild.get_channel(general_channel_id)
            lobby_channel = guild.get_channel(lobby_channel_id)
            team1_channel = guild.get_channel(team1_channel_id)
            team2_channel = guild.get_channel(team2_channel_id)

            for player in team1["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                try:
                    await user.move_to(lobby_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

            for player in team2["players"]:
                print(player)
                discord_user = player.get("discord_user")
                if not discord_user:
                    continue
                print(discord_user)
                discord_user_id = discord_user.get("user_id")
                user = guild.get_member(int(discord_user_id))
                print(user)
                if not user:
                    continue
                try:
                    await user.move_to(lobby_channel)
                except discord.errors.HTTPException as e:
                    print(e)
                    continue

        except httpx.HTTPError as e:
            print(e)

    async def on_round_end(self, data):
        print("Round end")

    async def on_side_picked(self, data):
        print("Side picked")

    async def on_map_picked(self, data):
        print("Map picked")

    async def on_map_vetoed(self, data):
        print("Map vetoed")
