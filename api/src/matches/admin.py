from django.contrib import admin

from matches.models import Map, Match, MapBan, MapPool, MatchConfig, MapPick


class MatchAdmin(admin.ModelAdmin):
    list_filter = ("status", "created_at", "updated_at")
    search_fields = (
        "team1__name",
        "team2__name",
        "status",
        "winner_team__name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("id", "created_at", "updated_at")


class MatchConfigAdmin(admin.ModelAdmin):
    list_filter = (
        "game_mode",
        "type",
        "clinch_series",
        "max_players",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "game_mode",
        "type",
        "clinch_series",
        "max_players",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("id", "created_at", "updated_at")


class MapAdmin(admin.ModelAdmin):
    list_filter = ("guild", "created_at", "updated_at")
    search_fields = ("name", "guild__name", "guild__id", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


class MapPoolAdmin(admin.ModelAdmin):
    list_filter = ("guild__name", "created_at", "updated_at")
    search_fields = ("name", "guild__name", "guild__id", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


class MapBanAdmin(admin.ModelAdmin):
    list_filter = ("created_at", "updated_at")
    search_fields = ("created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


class MapPickAdmin(MapBanAdmin):
    pass


# Register your models here.
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchConfig, MatchConfigAdmin)
admin.site.register(Map, MapAdmin)
admin.site.register(MapPool, MapPoolAdmin)
admin.site.register(MapBan, MapBanAdmin)
admin.site.register(MapPick, MapPickAdmin)
