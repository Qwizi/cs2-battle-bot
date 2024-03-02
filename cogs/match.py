import json
import os
import discord
from discord.ext import commands, tasks
import httpx

from utils import (
    create_match,
    get_connect_account_link,
    get_curent_match,
    get_match,
    get_teams_autocomplete,
    load_match,
)

guild_id = 639034263999741953
info_channel_id = 1210935599972749312
status_message_id = 1213212463563280454
general_channel_id = 1211078909127561257
lobby_channel_id = 1211059521762492486
team1_channel_id = 1211059841993281537
team2_channel_id = 1211059895202484344


class MatchView(
    discord.ui.View
):  # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(
        label="Start!", style=discord.ButtonStyle.primary, emoji="🚀"
    )  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        try:
            response = await load_match()
        except httpx.HTTPError as e:
            print(e)
            await interaction.response.send_message(
                "Failed to start match", ephemeral=True
            )
        else:
            await interaction.response.send_message("Pomyślnie załadowano mecz!")


class MatchCog(commands.Cog):
    def __init__(self, bot, pubsub):
        self.bot = bot
        self.pubsub = pubsub
        self.listen_events.start()

    match = discord.SlashCommandGroup(
        name="match", description="Commands for managing matches"
    )

    @match.command(guild_ids=[guild_id])
    async def connect(self, ctx: discord.ApplicationContext):
        connect_account_link = get_connect_account_link()
        await ctx.respond(f"[Połącz konto]({connect_account_link})", ephemeral=True)

    @match.command(guild_ids=[guild_id])
    async def create(
        self,
        ctx: discord.ApplicationContext,
        shuffle_teams: discord.Option(bool, default=False, name="shuffle_teams"),  # type: ignore
        maplist: discord.Option(str, default="de_mirage,de_nuke"),  # type: ignore
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
        if len(members) < 2:
            await ctx.followup.send(
                "You need at least 2 players to create a match.", ephemeral=True
            )
            return
        try:
            discord_users_ids = [member.id for member in members]
            maplist = maplist.split(",")
            webhook_url = f"{os.environ.get('API_URL')}/api/matches/webhook/"
            api_token = os.environ.get("API_TOKEN")
            match_data = {
                "discord_users_ids": discord_users_ids,
                "maplist": maplist,
                "shuffle_teams": shuffle_teams,
                "cvars": {
                    "matchzy_remote_log_url": webhook_url,
                    "matchzy_remote_log_header_key": "X-Api-Key",
                    "matchzy_remote_log_header_value": api_token,
                },
            }
            created_match, created_match_response = await create_match(match_data)
            team1 = created_match.get("team1")
            team2 = created_match.get("team2")

            team1_players = team1.get("players")
            team2_players = team2.get("players")

            team1_names = [
                f"<@{player.get('discord_user').get('user_id')}>"
                for player in team1_players
            ]
            team2_names = [
                f"<@{player.get('discord_user').get('user_id')}>"
                for player in team2_players
            ]

            print(created_match)
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
                name=team2.get("name", "Team 2"),
                value=f"{', '.join(team2_names)}",
                inline=False,
            )
            embed.add_field(name="Mapy", value=f"{', '.join(maplist)}", inline=False)

        except httpx.HTTPStatusError as e:
            data = e.response.json()
            if "Discord user" in data.get("message"):
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
        else:
            await ctx.followup.send(embed=embed, view=MatchView())

    @tasks.loop(seconds=5)
    async def listen_events(self):
        print("listening")
        message = self.pubsub.get_message()
        while message is not None:
            if message["type"] == "pmessage":
                data = message["data"].decode("utf-8")
                data = json.loads(data)
                event = data.get("event")
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
            match, match_response = await get_match(1)
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
