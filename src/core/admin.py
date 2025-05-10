from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.socialaccount.providers.openid.models import OpenIDStore, OpenIDNonce
from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin, \
    SocialAppAdmin as BaseSocialAppAdmin, SocialTokenAdmin as BaseSocialTokenAdmin
from allauth.socialaccount.providers.openid.admin import OpenIDStoreAdmin as BaseOpenIDStoreAdmin, \
    OpenIDNonceAdmin as BaseOpenIDNonceAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from guardian.admin import GuardedModelAdmin

from accounts.models import Account

# Register your models here.

ser = get_user_model()


admin.site.unregister(EmailAddress)
admin.site.unregister(Group)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(OpenIDStore)
admin.site.unregister(OpenIDNonce)


@admin.register(SocialAccount)
class SocialAccountAdmin(BaseSocialAccountAdmin, ModelAdmin):
    pass


@admin.register(SocialApp)
class SocialAppAdmin(BaseSocialAppAdmin, ModelAdmin):
    pass


@admin.register(SocialToken)
class SocialTokenAdmin(BaseSocialTokenAdmin, ModelAdmin):
    pass


@admin.register(OpenIDStore)
class OpenIDStoreAdmin(BaseOpenIDStoreAdmin, ModelAdmin):
    pass


@admin.register(OpenIDNonce)
class OpenIDNonceAdmin(BaseOpenIDNonceAdmin, ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(BaseUserAdmin, ModelAdmin, GuardedModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm