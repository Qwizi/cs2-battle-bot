from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, View
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django_htmx.http import HttpResponseLocation

from guilds.models import Guild

# Create your views here.

class GuildListView(ListView):
    model = Guild
    template_name = 'guilds/list.html'
    context_object_name = 'guilds'
    paginate_by = 10

    def get_queryset(self):
        # Filter the queryset to only include guilds that the user is a member of
        # Assuming you have a ManyToMany relationship between User and Guild
        # and the related name is 'members'
        # You can adjust the filter according to your model structure
        # For example, if you have a ManyToMany field named 'members' in the Guild model

        return Guild.objects.filter(members=self.request.user).order_by('name')
    


class SelectGuildView(View):
    def post(self, request, *args, **kwargs):
        guild_id = request.POST.get("guild_id")
        if guild_id:
            try:
                guild = Guild.objects.get(id=guild_id, members=request.user)
                request.session['selected_guild_id'] = guild.id
            except Guild.DoesNotExist:
                # Handle case where guild doesn't exist or user is not a member
                pass # Optionally, add a message to the user

        if request.htmx:
            # If it's an HTMX request, perform a client-side redirect using HX-Location.
            # The context fetching for selected_guild and user_guilds was for the 
            # previously commented-out render_to_string approach and is not strictly 
            # needed for this redirect, but left for now.
            selected_guild_id = request.session.get('selected_guild_id')
            selected_guild = None
            if selected_guild_id:
                try:
                    selected_guild = Guild.objects.get(id=selected_guild_id)
                except Guild.DoesNotExist:
                    pass # Or handle error

            user_guilds = Guild.objects.filter(members=request.user).order_by('name')

            return HttpResponseLocation(request.META.get('HTTP_REFERER', '/'))
        else:
            # For non-HTMX requests, redirect as before
            return redirect(request.META.get('HTTP_REFERER', '/'))


class GuildDetailView(DetailView):
    model = Guild
    template_name = 'guilds/detail.html'
    context_object_name = 'guild'
    pk_url_kwarg = "pk"