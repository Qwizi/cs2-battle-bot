import pytest

from accounts.factories import UserFactory, SocialAccountFactory


@pytest.mark.django_db
@pytest.fixture
def user():
    _user = UserFactory()
    _social_account = SocialAccountFactory(user=_user)
    return _user, _social_account
