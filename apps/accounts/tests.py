import pytest
from rest_framework.test import APIClient

from apps.users.models import User

from .models import Account

ACCOUNTS_URL = "/api/v1/accounts/"


@pytest.fixture
def user_a():
    return User.objects.create_user(email="a@example.com", password="StrongPass123!")


@pytest.fixture
def user_b():
    return User.objects.create_user(email="b@example.com", password="StrongPass123!")


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def client_b(user_b):
    client = APIClient()
    client.force_authenticate(user=user_b)
    return client


@pytest.mark.django_db
def test_unauthenticated_request_rejected():
    client = APIClient()
    response = client.get(ACCOUNTS_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_account(client_a):
    response = client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["name"] == "Main Bank"


@pytest.mark.django_db
def test_account_is_owned_by_creator(client_a, user_a):
    client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    account = Account.objects.get(name="Main Bank")
    assert account.user == user_a


@pytest.mark.django_db
def test_user_cannot_see_other_users_accounts(client_a, client_b):
    create_resp = client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    account_id = create_resp.data["id"]

    list_resp = client_b.get(ACCOUNTS_URL)
    assert list_resp.data["count"] == 0

    detail_resp = client_b.get(f"{ACCOUNTS_URL}{account_id}/")
    assert detail_resp.status_code == 404


@pytest.mark.django_db
def test_user_cannot_update_other_users_account(client_a, client_b):
    create_resp = client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    account_id = create_resp.data["id"]

    update_resp = client_b.patch(
        f"{ACCOUNTS_URL}{account_id}/", {"name": "Hijacked"}, format="json"
    )
    assert update_resp.status_code == 404


@pytest.mark.django_db
def test_update_own_account(client_a):
    create_resp = client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    account_id = create_resp.data["id"]

    update_resp = client_a.patch(
        f"{ACCOUNTS_URL}{account_id}/", {"name": "Renamed Bank"}, format="json"
    )
    assert update_resp.status_code == 200
    assert update_resp.data["name"] == "Renamed Bank"


@pytest.mark.django_db
def test_negative_initial_balance_rejected(client_a):
    response = client_a.post(
        ACCOUNTS_URL,
        {"name": "Bad Account", "account_type": "CASH", "initial_balance": "-50.00"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_duplicate_account_name_rejected_for_same_user(client_a):
    client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "BANK", "initial_balance": "1000.00"},
        format="json",
    )
    response = client_a.post(
        ACCOUNTS_URL,
        {"name": "Main Bank", "account_type": "CASH", "initial_balance": "500.00"},
        format="json",
    )
    assert response.status_code == 400
