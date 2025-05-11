from django import forms
from django.db.models import Q  # Corrected import
from .models import Map, MapPool

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ["name", "tag"]

class MapPoolForm(forms.ModelForm):
    class Meta:
        model = MapPool
        fields = ["name", "maps"]
        widgets = {
            'maps': forms.CheckboxSelectMultiple,  # Explicitly use CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        guild = kwargs.pop('guild', None)
        super().__init__(*args, **kwargs)
        
        current_maps_queryset = Map.objects.none()
        if guild:
            current_maps_queryset = Map.objects.filter(
                Q(guild=guild) | Q(guild__isnull=True)
            ).distinct()
        else:
            # Default to global maps if no specific guild context
            current_maps_queryset = Map.objects.filter(guild__isnull=True).distinct()

        self.fields['maps'].queryset = current_maps_queryset
        # Make maps field not required as selection is dynamic and can be empty initially
        # The actual selection will be handled by JS updating the checkboxes
        self.fields['maps'].required = False
