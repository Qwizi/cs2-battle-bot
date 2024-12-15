import factory
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda a: f"{a.username}@website.com")


class SocialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialAccount

    user = factory.SubFactory(UserFactory)
    provider = "discord"
    uid = factory.Sequence(lambda n: f"uid{n}")
    extra_data = factory.LazyAttribute(lambda o: {"username": o.user.username})
