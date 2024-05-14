from django.urls import include, path

from accounts.views import AccountConnectLinkView

urlpatterns = [
    path("", include("matches.urls")),
    path("", include("servers.urls")),
    path("", include("players.urls")),
    path("", include("guilds.urls")),
    path(
        "account-connect-link",
        AccountConnectLinkView.as_view(),
        name="account-connect-link",
    ),
]
