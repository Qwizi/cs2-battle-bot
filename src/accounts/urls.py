from django.urls import path

from accounts.views import AccountListView


urlpatterns = [
    path("", AccountListView.as_view(), name="users_list"),
]