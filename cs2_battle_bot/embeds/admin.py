from django.contrib import admin

from embeds.models import Embed, EmbedField

# Register your models here.
admin.site.register(Embed)
admin.site.register(EmbedField)