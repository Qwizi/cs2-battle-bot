from django.contrib import admin

from guilds.models import Guild


class GuildAdmin(admin.ModelAdmin):
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


# Register your models here.
admin.site.register(Guild, GuildAdmin)
