from rest_framework import routers

from players.views import (
    PlayerViewSet,
    TeamViewSet,
    DiscordUserViewSet,
    SteamUserViewSet,
)

router = routers.SimpleRouter()

router.register(r"players", PlayerViewSet)
router.register(r"teams", TeamViewSet)
router.register(r"discord-users", DiscordUserViewSet)
router.register(r"steam-users", SteamUserViewSet)

urlpatterns = router.urls
