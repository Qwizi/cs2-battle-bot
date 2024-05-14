from rest_framework import routers
from matches import views

router = routers.SimpleRouter()
router.register(r"matches", views.MatchViewSet, basename="match")
router.register(r"maps", views.MapViewSet, basename="map")

urlpatterns = router.urls
