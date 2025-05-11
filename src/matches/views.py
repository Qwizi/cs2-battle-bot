from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import models
from django_htmx.http import HttpResponseLocation
from matches.models import Match, MatchConfig, Cvar
from guilds.models import Guild
from .forms import MatchCreateForm, MatchConfigForm, CvarForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView

class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/list.html'
    context_object_name = 'matches'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Match.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return Match.objects.none()
        else:
            return Match.objects.none()

class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchCreateForm
    template_name = 'matches/form.html'

    def get_success_url(self):
        return reverse_lazy('matches:match-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if not selected_guild_id:
            form.add_error(None, "A guild must be selected to create a match.")
            return self.form_invalid(form)

        try:
            guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
            form.instance.guild = guild
        except Guild.DoesNotExist:
            form.add_error(None, "Selected guild not found or you are not a member.")
            return self.form_invalid(form)
        
        response = super().form_valid(form)

        if self.request.htmx:
            return HttpResponseLocation(self.get_success_url())
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            response.status_code = 422
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New Match"
        return context

class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'matches/detail.html'
    context_object_name = 'match'

class MatchUpdateView(LoginRequiredMixin, UpdateView):
    model = Match
    form_class = MatchCreateForm
    template_name = 'matches/form.html'
    context_object_name = 'match'

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return queryset.filter(guild=guild)
            except Guild.DoesNotExist:
                return queryset.none()
        return queryset.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('matches:match-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            return HttpResponseLocation(self.get_success_url())
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            response.status_code = 422
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match_identifier = self.object.name if hasattr(self.object, 'name') and self.object.name else self.object.pk
        context['form_title'] = f"Edit Match: {match_identifier}"
        return context

class MatchDeleteView(LoginRequiredMixin, DeleteView):
    model = Match
    template_name = 'matches/confirm_delete.html'
    context_object_name = 'match'
    success_url = reverse_lazy('matches:list')

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return queryset.filter(guild=guild)
            except Guild.DoesNotExist:
                return queryset.none()
        return queryset.none()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponseLocation(success_url)
        return redirect(success_url)

class MatchConfigListView(LoginRequiredMixin, ListView):
    model = MatchConfig
    template_name = 'matches/configs/list.html'
    context_object_name = 'configs'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return MatchConfig.objects.filter(guild=guild)
            except Guild.DoesNotExist:
                return MatchConfig.objects.none()
        return MatchConfig.objects.filter(guild__isnull=True)

class MatchConfigDetailView(LoginRequiredMixin, DetailView):
    model = MatchConfig
    template_name = 'matches/configs/detail.html'
    context_object_name = 'config'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = MatchConfig.objects.all()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

class MatchConfigCreateView(LoginRequiredMixin, CreateView):
    model = MatchConfig
    form_class = MatchConfigForm
    template_name = 'matches/configs/form.html'
    success_url = reverse_lazy('matches:config-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                kwargs['guild'] = Guild.objects.get(id=selected_guild_id, members=self.request.user)
            except Guild.DoesNotExist:
                kwargs['guild'] = None
        else:
            kwargs['guild'] = None
        return kwargs

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                form.instance.guild = guild
            except Guild.DoesNotExist:
                form.instance.guild = None
        else:
            form.instance.guild = None
        
        super().form_valid(form)
        if self.request.htmx:
            return HttpResponseLocation(self.success_url)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New Match Configuration"
        return context

class MatchConfigUpdateView(LoginRequiredMixin, UpdateView):
    model = MatchConfig
    form_class = MatchConfigForm
    template_name = 'matches/configs/form.html'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = MatchConfig.objects.all()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        selected_guild_id = self.request.session.get('selected_guild_id')
        if self.object.guild:
            kwargs['guild'] = self.object.guild
        elif selected_guild_id:
            try:
                kwargs['guild'] = Guild.objects.get(id=selected_guild_id, members=self.request.user)
            except Guild.DoesNotExist:
                kwargs['guild'] = None
        else:
            kwargs['guild'] = None
        return kwargs

    def get_success_url(self):
        return reverse_lazy('matches:config-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.htmx:
            return HttpResponseLocation(self.get_success_url())
        return redirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit Match Configuration: {self.object.name}"
        return context

class MatchConfigDeleteView(LoginRequiredMixin, DeleteView):
    model = MatchConfig
    template_name = 'matches/configs/confirm_delete.html'
    success_url = reverse_lazy('matches:config-list')
    context_object_name = 'config'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = MatchConfig.objects.all()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        if self.request.htmx:
            return HttpResponseLocation(success_url)
        return redirect(success_url)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponseLocation(success_url)
        return redirect(success_url)

class CvarListView(LoginRequiredMixin, ListView):
    model = Cvar
    template_name = 'matches/cvars/list.html'
    context_object_name = 'cvars'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Cvar.objects.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return Cvar.objects.filter(guild__isnull=True)
        return Cvar.objects.filter(guild__isnull=True)

class CvarDetailView(LoginRequiredMixin, DetailView):
    model = Cvar
    template_name = 'matches/cvars/detail.html'
    context_object_name = 'cvar'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

class CvarCreateView(LoginRequiredMixin, CreateView):
    model = Cvar
    form_class = CvarForm
    template_name = 'matches/cvars/form.html'

    def get_success_url(self):
        return reverse_lazy('matches:cvar-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                form.instance.guild = guild
            except Guild.DoesNotExist:
                form.instance.guild = None
        else:
            form.instance.guild = None

        response = super().form_valid(form)
        if self.request.htmx:
            return HttpResponseLocation(self.get_success_url())
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New CVar"
        return context

class CvarUpdateView(LoginRequiredMixin, UpdateView):
    model = Cvar
    form_class = CvarForm
    template_name = 'matches/cvars/form.html'
    context_object_name = 'cvar'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

    def get_success_url(self):
        return reverse_lazy('matches:cvar-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            return HttpResponseLocation(self.get_success_url())
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit CVar: {self.object.name}"
        return context

class CvarDeleteView(LoginRequiredMixin, DeleteView):
    model = Cvar
    template_name = 'matches/cvars/confirm_delete.html'
    context_object_name = 'cvar'
    success_url = reverse_lazy('matches:cvar-list')

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        qs = super().get_queryset()
        if selected_guild_id:
            try:
                guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return qs.filter(models.Q(guild=guild) | models.Q(guild__isnull=True))
            except Guild.DoesNotExist:
                return qs.filter(guild__isnull=True)
        return qs.filter(guild__isnull=True)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponseLocation(success_url)
        return redirect(success_url)
