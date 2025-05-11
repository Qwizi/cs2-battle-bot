from django.contrib import admin
from unfold.admin import ModelAdmin

from maps.models import Map, MapPool

# Register your models here.
@admin.register(Map)
class MapAdmin(ModelAdmin):
    list_display = ('id', 'name', 'tag', 'guild')
    search_fields = ('name', 'tag')
    list_filter = ('guild',)
    ordering = ('name',)
    list_per_page = 20
    list_select_related = ('guild',)
    raw_id_fields = ('guild',)


@admin.register(MapPool)
class MapPoolAdmin(ModelAdmin):
    list_display = ('id', 'name', 'guild')
    search_fields = ('name',)
    list_filter = ('guild',)
    ordering = ('name',)
    list_per_page = 20
    list_select_related = ('guild',)
    raw_id_fields = ('guild',)