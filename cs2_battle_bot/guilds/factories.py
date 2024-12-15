import factory

from accounts.factories import UserFactory
from guilds.models import Guild


class GuildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Guild

    name = factory.Faker('name')
    guild_id = factory.Faker('uuid4')
    owner = factory.SubFactory(UserFactory)
    lobby_channel = factory.Faker('uuid4')
    team1_channel = factory.Faker('uuid4')
    team2_channel = factory.Faker('uuid4')
    created_at = factory.Faker('date_time_this_year')
    updated_at = factory.Faker('date_time_this_year')
