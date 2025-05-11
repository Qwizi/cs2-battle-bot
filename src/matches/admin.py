from django.contrib import admin
from unfold.admin import ModelAdmin
from matches.models import Match, MatchConfig, Cvar, MatchConfigCvar

@admin.register(Match)
class MatchAdmin(ModelAdmin):
    list_display = ('id', 'status', 'team1', 'team2', 'config')
    search_fields = ('team1__name', 'team2__name')
    list_filter = ('status',)
    ordering = ('-id',)
    list_per_page = 20
    list_select_related = ('team1', 'team2', 'config')
    raw_id_fields = ('team1', 'team2', 'config')


@admin.register(MatchConfig)
class MatchConfigAdmin(ModelAdmin):
    list_display = ('id', 'name', 'type', 'map_sides')
    search_fields = ('name',)
    list_filter = ('type',)
    ordering = ('-id',)
    list_per_page = 20
    list_select_related = ()
    raw_id_fields = ()
    autocomplete_fields = ()  # Removed 'map_sides'
    prepopulated_fields = {'name': ('type',)}


@admin.register(Cvar)
class CvarAdmin(ModelAdmin):
    list_display = ('id', 'name', 'value_type')  # Changed 'value' to 'value_type'
    search_fields = ('name',)
    list_filter = ()
    ordering = ('-id',)
    list_per_page = 20
    list_select_related = ()
    raw_id_fields = ()

@admin.register(MatchConfigCvar)
class MatchConfigCvarAdmin(ModelAdmin):
    list_display = ('id', 'match_config', 'cvar', 'value')
    search_fields = ('match_config__name', 'cvar__name')
    list_filter = ('match_config',)
    ordering = ('-id',)
    list_per_page = 20
    list_select_related = ('match_config', 'cvar')
