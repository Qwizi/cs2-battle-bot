\
from django.conf import settings
from .models import Guild

def guild_context(request):
    context = {'bot_invite_url': settings.DISCORD_BOT_INVITE_URL}
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_guilds = Guild.objects.filter(members=request.user).order_by('name')
        selected_guild_id = request.session.get('selected_guild_id')
        selected_guild = None
        
        if selected_guild_id:
            try:
                selected_guild = Guild.objects.get(id=selected_guild_id, members=request.user)
            except Guild.DoesNotExist:
                # Clear session if guild doesn't exist or user is no longer a member
                request.session.pop('selected_guild_id', None)
        else:
            # If no guild is selected, set the first one as default if available
            if user_guilds.exists():
                selected_guild = user_guilds.first()
                request.session['selected_guild_id'] = selected_guild.id
        
        context.update({
            'user_guilds': user_guilds,
            'selected_guild': selected_guild,
        })
    return context
