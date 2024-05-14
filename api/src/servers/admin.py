from django.contrib import admin

from servers.models import Server

# Register your models here.


class AdminServer(admin.ModelAdmin):
    readonly_fields = ("id", "created_at", "updated_at")


admin.site.register(Server, AdminServer)
