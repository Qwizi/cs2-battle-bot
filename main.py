import os
import discord
from dotenv import load_dotenv
import redis
from cogs.match import MatchCog

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# @tasks.loop(seconds=5)
# async def listen_events():
#     _redis = redis.Redis(host="redis", port=6379, db=0)
#     print("listening")
#     pubsub = _redis.pubsub()
#     pubsub.subscribe("event.*")
#     for message in pubsub.listen():
#         print(message)


# @listen_events.before_loop
# async def before_listen_events():
#     await bot.wait_until_ready()


_redis = redis.StrictRedis(host="redis", port=6379, db=0)

pubsub = _redis.pubsub()
pubsub.psubscribe("event.*")
bot.add_cog(MatchCog(bot, pubsub))
bot.run(os.environ.get("TOKEN"))

# @bot.slash_command(guild_ids=[guild_id])
# async def losuj(ctx):
#     if ctx.author.voice is None:
#         await ctx.send("You're not in a voice channel.")
#         return
#     voice_channel = ctx.author.voice.channel

#     # Fetch the members in the voice channel
#     members = voice_channel.members

#     print(members)
#     # Shuffle the list of members
#     random.shuffle(members)

#     # Split the list of members into two teams
#     num_members = len(members)
#     middle_index = num_members // 2
#     team1 = members[:middle_index]
#     team2 = members[middle_index:]

#     # Create a list of member names for each team
#     team1_names = [member.name for member in team1]
#     team2_names = [member.name for member in team2]
#     # Send the list of member names as a response
#     await ctx.send(
#         f"Team 1: {', '.join(team1_names)} \nTeam 2: {', '.join(team2_names)}"
#     )


# @bot.slash_command(guild_ids=[guild_id])
# async def connect(ctx):
#     await ctx.send("[Połącz konto](https://cs2.sharkservers.pl/accounts/discord/)")


# @bot.slash_command(guild_ids=[guild_id])
# async def create(
#     ctx,
#     team1_name: discord.Option(str, default="Team1"),
#     team2_name: discord.Option(str, default="Team2"),
#     maplist: discord.Option(str, default="de_mirage,de_nuke"),
# ):
#     await ctx.defer()
#     maplist = maplist.split(",")
#     if ctx.author.voice is None:
#         await ctx.send("You're not in a voice channel.")
#         return
#     # Fetch the members in the voice channel
#     voice_channel = ctx.author.voice.channel
#     members = voice_channel.members
#     async with httpx.AsyncClient(base_url=os.environ.get("API_URL")) as client:
#         if len(members) <= 1:
#             await ctx.followup.send(
#                 "Potrzebujesz przynajmniej 2 graczy do utworzenia meczu."
#             )
#             return
#         players_response = await client.get("/players/")
#         players_steamids = []
#         if players_response.status_code == 200:
#             players = players_response.json()
#             players_ids = [player["discord_user"]["user_id"] for player in players]
#             players_steamids = [
#                 {
#                     str(player["steam_user"]["steamid64"]): player["discord_user"][
#                         "user_id"
#                     ]
#                 }
#                 for player in players
#             ]
#             print(players_steamids)
#             for member in members:
#                 if str(member.id) not in players_ids:
#                     await ctx.followup.send(
#                         f"Użytkownik <@{member.id}> nie jest zarejestrowany w bazie danych. Połącz konto na [stronie](https://cs2.sharkservers.pl/accounts/discord/)"
#                     )
#                     # remove member from list
#                     members.remove(member)
#         response = await client.post(
#             "/matches/",
#             json={
#                 "discord_users_ids": [member.id for member in members],
#                 "team1_name": team1_name,
#                 "team2_name": team2_name,
#                 "maplist": maplist,
#             },
#         )
#         data = response.json()
#         if response.status_code == 201:
#             team1 = data.get("team1")
#             team2 = data.get("team2")

#             if not team1 or not team2:
#                 await ctx.followup.send("Brakuje graczy do utworzenia meczu.")
#                 return
#             team1_names = []

#             for key, value in team1["players"].items():
#                 for steamid in players_steamids:
#                     for k, v in steamid.items():
#                         if k == key:
#                             team1_names.append(f"<@{v}>")
#                             break
#             team2_names = []
#             for key, value in team2["players"].items():
#                 for steamid in players_steamids:
#                     for k, v in steamid.items():
#                         if k == key:
#                             team2_names.append(f"<@{v}>")
#                             break

#             embed = discord.Embed(
#                 title="Mecz utworzony!",
#                 description="Mecz został utworzony.",
#                 color=discord.Colour.blurple(),  # Pycord provides a class with default colors you can choose from
#             )
#             embed.add_field(
#                 name=team1.get("name", "Team 1"),
#                 value=f"{', '.join(team1_names)}",
#                 inline=False,
#             )
#             embed.add_field(
#                 name=team2.get("name", "Team 2"),
#                 value=f"{', '.join(team2_names)}",
#                 inline=False,
#             )
#             embed.add_field(name="Mapy", value=f"{', '.join(maplist)}", inline=False)
#             await ctx.followup.send("Match created", embed=embed)
#         else:
#             await ctx.followup.send("Error creating match")
