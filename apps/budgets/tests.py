from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.categories.models import Category
from apps.transactions.models import Transaction
from apps.users.models import User

from .models import Budget

BUDGETS_URL = "/api/v1/budgets/"


@pytest.fixture
def user_a():
    return User.objects.create_user(email="a@example.com", password="StrongPass123!")


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def food_category():
    return Category.objects.get(user__isnull=True, name="Food")


@pytest.fixture
def account_a(user_a):
    return Account.objects.create(
        user=user_a, name="Bank A", account_type="BANK", initial_balance="1000.00"
    )


@pytest.mark.django_db
def test_create_budget(client_a, food_category):
    response = client_a.post(
        BUDGETS_URL,
        {"category": food_category.id, "amount": "8000.00", "month": 8, "year": 2026},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["spent"] == "0.00" or response.data["spent"] == 0


@pytest.mark.django_db
def test_duplicate_budget_rejected(client_a, food_category):
    client_a.post(
        BUDGETS_URL,
        {"category": food_category.id, "amount": "8000.00", "month": 8, "year": 2026},
        format="json",
    )
    response = client_a.post(
        BUDGETS_URL,
        {"category": food_category.id, "amount": "9000.00", "month": 8, "year": 2026},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_negative_budget_amount_rejected(client_a, food_category):
    response = client_a.post(
        BUDGETS_URL,
        {"category": food_category.id, "amount": "-100.00", "month": 8, "year": 2026},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_invalid_month_rejected(client_a, food_category):
    response = client_a.post(
        BUDGETS_URL,
        {"category": food_category.id, "amount": "100.00", "month": 13, "year": 2026},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_spending_calculation(client_a, user_a, account_a, food_category):
    budget = Budget.objects.create(
        user=user_a, category=food_category, amount="8000.00", month=8, year=2026
    )
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=food_category,
        amount="1200.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 5),
    )
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=food_category,
        amount="800.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 10),
    )
    # Transaction outside the budget's month should not count.
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=food_category,
        amount="500.00",
        transaction_type="EXPENSE",
        date=date(2026, 7, 20),
    )

    response = client_a.get(f"{BUDGETS_URL}{budget.id}/")
    assert response.data["spent"] == "2000.00"
    assert response.data["remaining"] == "6000.00"
    assert response.data["percentage_used"] == 25.0


@pytest.mark.django_db
def test_filter_budgets_by_month_year(client_a, user_a, food_category):
    Budget.objects.create(user=user_a, category=food_category, amount="8000.00", month=8, year=2026)
    salary = Category.objects.get(user__isnull=True, name="Rent")
    Budget.objects.create(user=user_a, category=salary, amount="15000.00", month=9, year=2026)

    response = client_a.get(BUDGETS_URL, {"month": 8, "year": 2026})
    assert response.data["count"] == 1
