from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from .models import Team
from .forms import TeamForm
from guilds.models import Guild
from accounts.models import Account
from django.db.models import Q

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/list.html'
    context_object_name = 'teams'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Team.objects.filter(guild=guild).distinct()
            except Guild.DoesNotExist:
                return Team.objects.none()
        return Team.objects.none()

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/detail.html'
    context_object_name = 'team'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(guild=guild).distinct()
            except Guild.DoesNotExist:
                return qs.none()
        return qs.none()

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/form.html'
    
    def get_success_url(self):
        return reverse_lazy('teams:team-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if not selected_guild_id:
            form.add_error(None, "A guild must be selected to create a team.")
            return self.form_invalid(form)

        try:
            guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
            form.instance.guild = guild
        except Guild.DoesNotExist:
            form.add_error(None, "Selected guild not found or you are not a member.")
            return self.form_invalid(form)

        # Process captain and players from POST data
        captain_id = self.request.POST.get('capitan')
        player_ids = self.request.POST.getlist('players')

        if not captain_id:
            form.add_error(None, "A captain must be selected.") # Or handle as a field-specific error on a dummy field if preferred
            return self.form_invalid(form)
        
        try:
            captain_account = guild.members.get(id=captain_id)
            form.instance.capitan = captain_account
        except Account.DoesNotExist:
            form.add_error(None, "Selected captain is not valid or not a member of the guild.")
            return self.form_invalid(form)

        # Save the instance to get a PK for M2M relations
        self.object = form.save(commit=False)
        self.object.capitan = captain_account # Assign captain before full save if not done by form.save()
        self.object.save() 

        # Process players
        valid_players = []
        if player_ids:
            for player_id in player_ids:
                try:
                    player_account = guild.members.get(id=player_id)
                    valid_players.append(player_account)
                except Account.DoesNotExist:
                    form.add_error(None, f"Selected player with ID {player_id} is not valid or not a member of the guild.")
                    # self.object.delete() # Optional: clean up partially created team
                    return self.form_invalid(form)
        
        # Add captain to players list if not already included
        if captain_account not in valid_players:
            valid_players.append(captain_account)

        self.object.players.set(valid_players)
        # No need to call super().form_valid(form) again if we manually save and handle M2M
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New Team"
        return context

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/form.html'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(guild=guild).distinct()
            except Guild.DoesNotExist:
                return qs.none()
        return qs.filter(capitan=self.request.user.account, is_temp=True, guild__isnull=True).distinct()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if not selected_guild_id:
            form.add_error(None, "A guild must be selected to create a team.")
            return self.form_invalid(form)

        try:
            guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
            form.instance.guild = guild
        except Guild.DoesNotExist:
            form.add_error(None, "Selected guild not found or you are not a member.")
            return self.form_invalid(form)

        # Process captain and players from POST data
        captain_id = self.request.POST.get('capitan')
        player_ids = self.request.POST.getlist('players')

        if not captain_id:
            form.add_error(None, "A captain must be selected.") # Or handle as a field-specific error on a dummy field if preferred
            return self.form_invalid(form)
        
        try:
            captain_account = guild.members.get(id=captain_id)
            form.instance.capitan = captain_account
        except Account.DoesNotExist:
            form.add_error(None, "Selected captain is not valid or not a member of the guild.")
            return self.form_invalid(form)

        # Save the instance to get a PK for M2M relations
        self.object = form.save(commit=False)
        self.object.capitan = captain_account # Assign captain before full save if not done by form.save()
        self.object.save() 

        # Process players
        valid_players = []
        if player_ids:
            for player_id in player_ids:
                try:
                    player_account = guild.members.get(id=player_id)
                    valid_players.append(player_account)
                except Account.DoesNotExist:
                    form.add_error(None, f"Selected player with ID {player_id} is not valid or not a member of the guild.")
                    # self.object.delete() # Optional: clean up partially created team
                    return self.form_invalid(form)
        
        # Add captain to players list if not already included
        if captain_account not in valid_players:
            valid_players.append(captain_account)

        self.object.players.set(valid_players)
        # No need to call super().form_valid(form) again if we manually save and handle M2M
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('teams:team-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit Team: {self.object.name}"
        return context

class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = 'teams/confirm_delete.html'
    success_url = reverse_lazy('teams:team-list')
    context_object_name = 'team'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(guild=guild).distinct()
            except Guild.DoesNotExist:
                return qs.none()
        return qs.filter(capitan=self.request.user.account, is_temp=True, guild__isnull=True).distinct()

class PlayerSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        selected_guild_id = request.session.get('selected_guild_id')
        search_context = request.GET.get('search_context', 'player') # 'captain' or 'player'

        if not selected_guild_id:
            return HttpResponse('<tr><td colspan="100%">A guild must be selected.</td></tr>', status=400)

        query = request.GET.get('user_query', '')

        try:
            guild = Guild.objects.get(id=selected_guild_id)
            if not guild.members.filter(id=request.user.id).exists():
                 return HttpResponse('<tr><td colspan="100%">You are not a member of this guild.</td></tr>', status=403)
            
            players = guild.members.filter(username__icontains=query)[:10]
        except Guild.DoesNotExist:
            players = Account.objects.none()
        
        html = render_to_string('teams/partials/player_search_results.html', 
                                {'players': players, 'search_context': search_context})
        return HttpResponse(html)
