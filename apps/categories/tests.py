import pytest
from rest_framework.test import APIClient

from apps.users.models import User

from .models import Category

CATEGORIES_URL = "/api/v1/categories/"


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
def test_default_categories_were_seeded():
    assert Category.objects.filter(user__isnull=True, name="Salary", category_type="INCOME").exists()
    assert Category.objects.filter(user__isnull=True, name="Food", category_type="EXPENSE").exists()


@pytest.mark.django_db
def test_list_includes_defaults_and_own_categories(client_a, user_a):
    Category.objects.create(user=user_a, name="Freelance", category_type="INCOME")
    response = client_a.get(CATEGORIES_URL)
    names = {item["name"] for item in response.data["results"]}
    assert "Salary" in names
    assert "Freelance" in names


@pytest.mark.django_db
def test_list_does_not_include_other_users_categories(client_a, client_b, user_b):
    Category.objects.create(user=user_b, name="Bonus", category_type="INCOME")
    response = client_a.get(CATEGORIES_URL)
    names = {item["name"] for item in response.data["results"]}
    assert "Bonus" not in names


@pytest.mark.django_db
def test_create_own_category(client_a):
    response = client_a.post(
        CATEGORIES_URL, {"name": "Freelance", "category_type": "INCOME"}, format="json"
    )
    assert response.status_code == 201
    assert response.data["is_default"] is False


@pytest.mark.django_db
def test_cannot_update_default_category(client_a):
    default_category = Category.objects.get(user__isnull=True, name="Food")
    response = client_a.patch(
        f"{CATEGORIES_URL}{default_category.id}/", {"name": "Hacked"}, format="json"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_cannot_update_other_users_category(client_a, client_b, user_b):
    category = Category.objects.create(user=user_b, name="Bonus", category_type="INCOME")
    response = client_a.patch(
        f"{CATEGORIES_URL}{category.id}/", {"name": "Hacked"}, format="json"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_duplicate_category_rejected_for_same_user(client_a):
    client_a.post(CATEGORIES_URL, {"name": "Side Hustle", "category_type": "INCOME"}, format="json")
    response = client_a.post(
        CATEGORIES_URL, {"name": "Side Hustle", "category_type": "INCOME"}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_invalid_category_type_rejected(client_a):
    response = client_a.post(
        CATEGORIES_URL, {"name": "Weird", "category_type": "SAVINGS"}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_filter_by_category_type(client_a):
    response = client_a.get(CATEGORIES_URL, {"category_type": "EXPENSE"})
    types = {item["category_type"] for item in response.data["results"]}
    assert types == {"EXPENSE"}
    assert "Salary" not in {item["name"] for item in response.data["results"]}
