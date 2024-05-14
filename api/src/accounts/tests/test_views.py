import pytest


@pytest.mark.django_db
def test_account_connect_link(client_with_api_key):
    response = client_with_api_key.get("/api/account-connect-link")
    assert response.status_code == 200
    assert response.data["link"] is not None
