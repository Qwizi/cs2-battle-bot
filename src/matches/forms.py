from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from .models import Match, MatchConfig, Cvar
from teams.models import Team
from maps.models import MapPool

class MatchCreateForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['config', 'team1', 'team2']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            # Further filter team1, team2, config based on selected guild or user permissions if necessary
            # For now, allowing all teams and configs
            self.fields['team1'].queryset = Team.objects.all() # Consider filtering by guild
            self.fields['team2'].queryset = Team.objects.all() # Consider filtering by guild
            self.fields['config'].queryset = MatchConfig.objects.all() # Consider filtering by guild

        # Add Tailwind CSS classes or use a widget rendering library like django-widget-tweaks
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input input-bordered w-full'})

class MatchConfigForm(forms.ModelForm):
    class Meta:
        model = MatchConfig
        fields = [
            'name',
            'map_pool',
            'game_mode',
            'type',
            'map_sides',
            'players_per_team',
            'shuffle_teams',
            'clinch_series',
            'cvars',
        ]
        widgets = {
            'map_sides': forms.HiddenInput(),
            'cvars': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Pop guild from kwargs if present, to be used for filtering MapPool
        guild = kwargs.pop('guild', None) 
        super().__init__(*args, **kwargs)

        if guild:
            self.fields['map_pool'].queryset = MapPool.objects.filter(guild=guild)
        elif self.instance and self.instance.guild: # For update view, if guild is already set
            self.fields['map_pool'].queryset = MapPool.objects.filter(guild=self.instance.guild)
        else:
            self.fields['map_pool'].queryset = MapPool.objects.none() # No guild, no map pools

class CvarForm(forms.ModelForm):
    class Meta:
        model = Cvar
        fields = ["name", "value_type", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # The template will have the <form> tag
        self.helper.layout = Layout(
            Field("name", wrapper_class="mb-4"),
            Field("value_type", wrapper_class="mb-4"),
            Field("description", wrapper_class="mb-4"),
        )
