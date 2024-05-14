from accounts import views
from django.urls import path


urlpatterns = [
    path("discord/", views.redirect_to_discord, name="redirect_to_discord"),
    path("discord/callback", views.discord_callback, name="discord_callback"),
    path("steam/", views.redirect_to_steam, name="redirect_to_steam"),
    path("steam/callback", views.steam_callback, name="steam_callback"),
    path("success/", views.success, name="success"),
]
