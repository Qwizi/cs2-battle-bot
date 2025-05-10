from django.contrib import admin
from django.http import Http404
from unfold.admin import ModelAdmin

from guilds.models import Guild
from guardian.admin import GuardedModelAdmin


class CaseInsensitivePKAdmin(GuardedModelAdmin):
    def get_object(self, request, object_id, from_field=None):
        qs = self.get_queryset(request)
        try:
            return qs.get(pk__iexact=object_id)
        except self.model.DoesNotExist:
            raise Http404(f"{self.model._meta.verbose_name} not found.")

@admin.register(Guild)
class GuildAdmin(ModelAdmin, CaseInsensitivePKAdmin):
    pass
