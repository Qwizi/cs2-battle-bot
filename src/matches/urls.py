from django.urls import path
from .views import (
    MatchCreateView, MatchListView, MatchDetailView,
    MatchUpdateView, MatchDeleteView,
    MatchConfigListView, MatchConfigDetailView, MatchConfigCreateView,
    MatchConfigUpdateView, MatchConfigDeleteView
)

app_name = 'matches'

urlpatterns = [
    path('create/', MatchCreateView.as_view(), name='match-create'),
    path('', MatchListView.as_view(), name='list'),
    path('<int:pk>/', MatchDetailView.as_view(), name='match-detail'),
    path('<int:pk>/edit/', MatchUpdateView.as_view(), name='match-update'),
    path('<int:pk>/delete/', MatchDeleteView.as_view(), name='match-delete'),

    # MatchConfig URLs - we will namespace them under 'configs/' within the 'matches' app
    path('configs/', MatchConfigListView.as_view(), name='config-list'),
    path('configs/create/', MatchConfigCreateView.as_view(), name='config-create'),
    path('configs/<str:pk>/', MatchConfigDetailView.as_view(), name='config-detail'),
    path('configs/<str:pk>/edit/', MatchConfigUpdateView.as_view(), name='config-edit'),
    path('configs/<str:pk>/delete/', MatchConfigDeleteView.as_view(), name='config-delete'),
]
