from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from .models import Match, MatchConfig, Cvar, MatchConfigCvar
from teams.models import Team
from maps.models import MapPool
import json

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
    cvars_json = forms.CharField(widget=forms.HiddenInput(), required=False) # Stores the selected CVars with their values as JSON

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
        ]
        widgets = {
            'map_sides': forms.HiddenInput(),
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
        
        # Initialize cvars_json with current MatchConfigCvar values
        if self.instance and self.instance.pk:
            config_cvars = self.instance.matchconfigcvar_set.all()
            cvars_data = {
                cc.cvar.pk: {'name': cc.cvar.name, 'value': cc.value, 'value_type': cc.cvar.value_type}
                for cc in config_cvars
            }
            self.initial['cvars_json'] = json.dumps(cvars_data)
        else:
            self.initial['cvars_json'] = json.dumps({})

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handling CVars from cvars_json
        if commit:
            instance.save() # Save the instance first
            
            # Clear existing MatchConfigCvar relations for this config
            instance.matchconfigcvar_set.all().delete()

            if self.cleaned_data.get('cvars_json'):
                cvars_data = json.loads(self.cleaned_data['cvars_json'])
                for cvar_id, cvar_info in cvars_data.items():
                    try:
                        cvar_instance = Cvar.objects.get(pk=cvar_id)
                        MatchConfigCvar.objects.create(
                            match_config=instance,
                            cvar=cvar_instance,
                            value=cvar_info['value']
                        )
                    except Cvar.DoesNotExist:
                        # Handle case where cvar_id is not found, though ideally UI prevents this
                        pass
        return instance

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
