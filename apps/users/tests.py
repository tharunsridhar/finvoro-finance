import pytest
from rest_framework.test import APIClient

from .models import User

REGISTER_URL = "/api/v1/auth/register/"
LOGIN_URL = "/api/v1/auth/login/"
ME_URL = "/api/v1/auth/me/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_creates_user(api_client):
    response = api_client.post(
        REGISTER_URL,
        {"email": "alice@example.com", "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 201
    assert User.objects.filter(email="alice@example.com").exists()
    assert "password" not in response.data


@pytest.mark.django_db
def test_register_duplicate_email_rejected(api_client):
    User.objects.create_user(email="alice@example.com", password="StrongPass123!")
    response = api_client.post(
        REGISTER_URL,
        {"email": "alice@example.com", "password": "AnotherPass123!"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens(api_client):
    User.objects.create_user(email="alice@example.com", password="StrongPass123!")
    response = api_client.post(
        LOGIN_URL,
        {"email": "alice@example.com", "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_invalid_password_rejected(api_client):
    User.objects.create_user(email="alice@example.com", password="StrongPass123!")
    response = api_client.post(
        LOGIN_URL,
        {"email": "alice@example.com", "password": "WrongPassword!"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_requires_authentication(api_client):
    response = api_client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_current_user(api_client):
    user = User.objects.create_user(email="alice@example.com", password="StrongPass123!")
    api_client.force_authenticate(user=user)
    response = api_client.get(ME_URL)
    assert response.status_code == 200
    assert response.data["email"] == "alice@example.com"
