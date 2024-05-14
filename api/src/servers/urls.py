from rest_framework import routers

from servers import views

router = routers.SimpleRouter()

router.register(r"servers", views.ServerViewSet)

urlpatterns = router.urls
