from django.shortcuts import render
from django.views.generic import ListView
from accounts.models import Account
from guilds.models import Guild


class AccountListView(ListView):
    model = Account
    template_name = 'accounts/list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        selected_guild_id = self.request.session.get('selected_guild_id')
        
        if selected_guild_id:
            try:
                # Fetch the selected guild, ensuring the user is a member,
                # similar to your guild_context processor.
                selected_guild = Guild.objects.get(id=selected_guild_id, members=self.request.user)
                
                # Now filter accounts based on this selected_guild.
                # This assumes your Guild model has a related manager named 'accounts'
                # (e.g., from a ForeignKey in Account to Guild with related_name='accounts',
                # or a ManyToManyField in Guild named 'accounts').
                return selected_guild.members.all()
            except Guild.DoesNotExist:
                # If the guild doesn't exist or the user is not a member,
                # return an empty queryset.
                return Account.objects.none()
        else:
            # If no guild is selected, return an empty queryset.
            # Adjust this logic if you want to show all accounts or handle it differently.
            return Account.objects.none()
