from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_htmx.http import HttpResponseLocation

from .models import Map, MapPool
from .forms import MapForm, MapPoolForm
from guilds.models import Guild

class MapListView(LoginRequiredMixin, ListView):
    model = Map
    template_name = 'maps/list.html' # We'll need to create this template
    context_object_name = 'maps'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                # Ensure the user is a member of the guild they are trying to access
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Map.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return Map.objects.none() # Or handle as an error
        return Map.objects.none() # No guild selected, show no maps or global maps if applicable

class MapDetailView(LoginRequiredMixin, DetailView):
    model = Map
    template_name = 'maps/detail.html' # We'll need to create this template
    context_object_name = 'map'

    def get_queryset(self):
        # Filter by guild to ensure user has access
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Map.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return Map.objects.none()
        return Map.objects.none()

class MapCreateView(LoginRequiredMixin, CreateView):
    model = Map
    form_class = MapForm
    template_name = 'maps/form.html' # We'll need to create this template
    
    def get_success_url(self):
        return reverse_lazy('maps:map-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if not selected_guild_id:
            form.add_error(None, "A guild must be selected to create a map.")
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
            response.status_code = 422 # Unprocessable Entity for HTMX
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New Map"
        return context

class MapUpdateView(LoginRequiredMixin, UpdateView):
    model = Map
    form_class = MapForm
    template_name = 'maps/form.html' # We'll need to create this template
    context_object_name = 'map'

    def get_queryset(self):
        # Filter by guild to ensure user has access
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Map.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return Map.objects.none()
        return Map.objects.none()

    def get_success_url(self):
        return reverse_lazy('maps:map-detail', kwargs={'pk': self.object.pk})

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
        context['form_title'] = f"Edit Map: {self.object.name}"
        return context

class MapDeleteView(LoginRequiredMixin, DeleteView):
    model = Map
    template_name = 'maps/confirm_delete.html' # We'll need to create this template
    success_url = reverse_lazy('maps:map-list')
    context_object_name = 'map'

    def get_queryset(self):
        # Filter by guild to ensure user has access
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return Map.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return Map.objects.none()
        return Map.objects.none()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            # For HTMX, we want to redirect the entire page to the list view
            # So we send a location response that HTMX will use to update the browser URL
            # and swap the body.
            return HttpResponseLocation(success_url) 
        return redirect(success_url)

# MapPool Views

class MapPoolListView(LoginRequiredMixin, ListView):
    model = MapPool
    template_name = 'maps/mappools/list.html'
    context_object_name = 'mappools'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return MapPool.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return MapPool.objects.none()
        return MapPool.objects.none()

class MapPoolDetailView(LoginRequiredMixin, DetailView):
    model = MapPool
    template_name = 'maps/mappools/detail.html'
    context_object_name = 'mappool'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return MapPool.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return MapPool.objects.none()
        return MapPool.objects.none()

class MapPoolCreateView(LoginRequiredMixin, CreateView):
    model = MapPool
    form_class = MapPoolForm
    template_name = 'maps/mappools/form.html'

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

    def get_success_url(self):
        return reverse_lazy('maps:mappool-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if not selected_guild_id:
            form.add_error(None, "A guild must be selected to create a map pool.")
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
        context['form_title'] = "Create New Map Pool"
        return context

class MapPoolUpdateView(LoginRequiredMixin, UpdateView):
    model = MapPool
    form_class = MapPoolForm
    template_name = 'maps/mappools/form.html'
    context_object_name = 'mappool'

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

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return MapPool.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return MapPool.objects.none()
        return MapPool.objects.none()

    def get_success_url(self):
        return reverse_lazy('maps:mappool-detail', kwargs={'pk': self.object.pk})

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
        context['form_title'] = f"Edit Map Pool: {self.object.name}"
        return context

class MapPoolDeleteView(LoginRequiredMixin, DeleteView):
    model = MapPool
    template_name = 'maps/mappools/confirm_delete.html'
    success_url = reverse_lazy('maps:mappool-list')
    context_object_name = 'mappool'

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                return MapPool.objects.filter(guild=selected_guild)
            except Guild.DoesNotExist:
                return MapPool.objects.none()
        return MapPool.objects.none()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if request.htmx:
            return HttpResponseLocation(success_url)
        return redirect(success_url)
