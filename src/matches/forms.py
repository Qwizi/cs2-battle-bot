from django import forms
from .models import Match, MatchConfig
from teams.models import Team
from guilds.models import Guild

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
            'game_mode',
            'type',
            'map_sides',
            'players_per_team',
            'shuffle_teams',
            'clinch_series',
            'cvars',
            # 'guild' is removed from here, will be set in the view
        ]
        widgets = {
            'map_sides': forms.Textarea(attrs={'rows': 3}),
            'cvars': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removed the loop that manually added CSS classes.
        # crispy-daisyui will now handle the styling.

        # Removed logic for handling the 'guild' field as it's no longer in the form

        # Example of how to set initial guild based on session or context (remains for reference)
        # if self.request and self.request.session.get('selected_guild_id'):
        #     try:
        #         selected_guild = Guild.objects.get(id=self.request.session.get('selected_guild_id'))
        #         # This would be for setting an initial value if the field were present
        #         # self.fields['guild'].initial = selected_guild 
        #     except Guild.DoesNotExist:
        #         pass
