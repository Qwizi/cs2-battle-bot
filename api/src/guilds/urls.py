from rest_framework.routers import SimpleRouter

from guilds.views import GuildViewSet

router = SimpleRouter()
router.register(r"guilds", GuildViewSet, basename="guilds")

urlpatterns = router.urls
