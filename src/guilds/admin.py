from django.contrib import admin
from unfold.admin import ModelAdmin

from guilds.models import Guild


# Register your models here.

@admin.register(Guild)
class GuildAdmin(ModelAdmin):
    pass
