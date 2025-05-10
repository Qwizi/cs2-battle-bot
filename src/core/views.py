from django.conf import settings
from django.shortcuts import render

# Create your views here.

def index(request):
    guilds = request.user.guilds.all() if request.user.is_authenticated else None
    bot_invite_url = settings.DISCORD_BOT_INVITE_URL
    return render(request, "home/index.html", {
        "guilds": guilds,
        "bot_invite_url": bot_invite_url,
    })