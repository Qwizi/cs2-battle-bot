from django.urls import path


from guilds.views import GuildListView, GuildDetailView, SelectGuildView

app_name = 'guilds'

urlpatterns = [
    path("select/", SelectGuildView.as_view(), name="select_guild"),
    path("<str:pk>", GuildDetailView.as_view(), name="guild_detail"),
    path("", GuildListView.as_view(), name="guild_list"),
]