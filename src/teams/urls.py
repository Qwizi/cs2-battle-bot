from django.urls import path
from .views import (
    TeamListView,
    TeamDetailView,
    TeamCreateView,
    TeamUpdateView,
    TeamDeleteView,
    PlayerSearchView,
)

app_name = 'teams'

urlpatterns = [
    path('', TeamListView.as_view(), name='team-list'),
    path('create/', TeamCreateView.as_view(), name='team-create'),
    path('search-players/', PlayerSearchView.as_view(), name='player-search'),
    path('<str:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('<str:pk>/update/', TeamUpdateView.as_view(), name='team-update'),
    path('<str:pk>/delete/', TeamDeleteView.as_view(), name='team-delete'),
    
]
