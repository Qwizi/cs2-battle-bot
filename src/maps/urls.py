from django.urls import path
from .views import (
    MapListView,
    MapDetailView,
    MapCreateView,
    MapUpdateView,
    MapDeleteView,
    MapSearchView,
    MapPoolListView,
    MapPoolDetailView,
    MapPoolCreateView,
    MapPoolUpdateView,
    MapPoolDeleteView,
)

app_name = 'maps'

urlpatterns = [
    path('', MapListView.as_view(), name='map-list'),
    path('search/', MapSearchView.as_view(), name='map-search'),
    path('pools/', MapPoolListView.as_view(), name='mappool-list'),
    path('pools/create/', MapPoolCreateView.as_view(), name='mappool-create'),
    path('pools/<str:pk>/', MapPoolDetailView.as_view(), name='mappool-detail'),
    path('pools/<str:pk>/update/', MapPoolUpdateView.as_view(), name='mappool-update'),
    path('pools/<str:pk>/delete/', MapPoolDeleteView.as_view(), name='mappool-delete'),
    path('create/', MapCreateView.as_view(), name='map-create'),
    path('<str:pk>/', MapDetailView.as_view(), name='map-detail'),
    path('<str:pk>/update/', MapUpdateView.as_view(), name='map-update'),
    path('<str:pk>/delete/', MapDeleteView.as_view(), name='map-delete'),

    
]
