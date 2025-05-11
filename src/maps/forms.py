from django import forms
from .models import Map, MapPool

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ["name", "tag"]

class MapPoolForm(forms.ModelForm):
    class Meta:
        model = MapPool
        fields = ["name", "maps"]

    def __init__(self, *args, **kwargs):
        # We need to get the guild from the view to filter the maps queryset
        # The view will need to pass `request` to the form kwargs
        # And the view will need to add `guild` to the form instance before saving
        # or ensure the guild is passed to the form for filtering.
        # For now, let's assume the view handles guild filtering for the queryset.
        guild = kwargs.pop('guild', None)
        super().__init__(*args, **kwargs)
        if guild:
            self.fields['maps'].queryset = Map.objects.filter(guild=guild)
        else:
            # If no guild, perhaps show no maps or all maps if that's desired (less likely for guild-specific pools)
            self.fields['maps'].queryset = Map.objects.none()
