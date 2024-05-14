from django.contrib import admin

from players.models import DiscordUser, Player, SteamUser, Team

# Register your models here.
admin.site.register(DiscordUser)
admin.site.register(SteamUser)
admin.site.register(Player)
admin.site.register(Team)
