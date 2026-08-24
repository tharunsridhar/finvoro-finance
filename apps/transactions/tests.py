from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.categories.models import Category
from apps.users.models import User

from .models import Transaction

TRANSACTIONS_URL = "/api/v1/transactions/"


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


@pytest.fixture
def account_a(user_a):
    return Account.objects.create(
        user=user_a, name="Bank A", account_type="BANK", initial_balance="1000.00"
    )


@pytest.fixture
def account_b(user_b):
    return Account.objects.create(
        user=user_b, name="Bank B", account_type="BANK", initial_balance="1000.00"
    )


@pytest.fixture
def salary_category():
    return Category.objects.get(user__isnull=True, name="Salary")


@pytest.fixture
def food_category():
    return Category.objects.get(user__isnull=True, name="Food")


@pytest.mark.django_db
def test_create_income_transaction(client_a, account_a, salary_category):
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": salary_category.id,
            "amount": "500.00",
            "transaction_type": "INCOME",
            "date": "2026-08-01",
            "description": "August salary",
        },
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_expense_transaction(client_a, account_a, food_category):
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": food_category.id,
            "amount": "50.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_negative_or_zero_amount_rejected(client_a, account_a, food_category):
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": food_category.id,
            "amount": "0.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_mismatched_category_type_rejected(client_a, account_a, salary_category):
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": salary_category.id,
            "amount": "50.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_cannot_use_another_users_account(client_a, account_b, food_category):
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_b.id,
            "category": food_category.id,
            "amount": "50.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    assert response.status_code == 400
    assert "account" in response.data


@pytest.mark.django_db
def test_cannot_use_another_users_private_category(client_a, client_b, account_a, user_b):
    private_category = Category.objects.create(user=user_b, name="Secret", category_type="EXPENSE")
    response = client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": private_category.id,
            "amount": "50.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    assert response.status_code == 400
    assert "category" in response.data


@pytest.mark.django_db
def test_user_cannot_see_other_users_transactions(
    client_a, client_b, account_a, account_b, food_category
):
    Transaction.objects.create(
        user=account_a.user,
        account=account_a,
        category=food_category,
        amount="50.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 2),
    )
    response = client_b.get(TRANSACTIONS_URL)
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_filter_by_transaction_type(client_a, account_a, salary_category, food_category):
    Transaction.objects.create(
        user=account_a.user,
        account=account_a,
        category=salary_category,
        amount="500.00",
        transaction_type="INCOME",
        date=date(2026, 8, 1),
    )
    Transaction.objects.create(
        user=account_a.user,
        account=account_a,
        category=food_category,
        amount="50.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 2),
    )
    response = client_a.get(TRANSACTIONS_URL, {"transaction_type": "EXPENSE"})
    assert response.data["count"] == 1
    assert response.data["results"][0]["transaction_type"] == "EXPENSE"


@pytest.mark.django_db
def test_filter_by_date_range(client_a, account_a, food_category):
    Transaction.objects.create(
        user=account_a.user,
        account=account_a,
        category=food_category,
        amount="10.00",
        transaction_type="EXPENSE",
        date=date(2026, 7, 15),
    )
    Transaction.objects.create(
        user=account_a.user,
        account=account_a,
        category=food_category,
        amount="20.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 15),
    )
    response = client_a.get(
        TRANSACTIONS_URL, {"start_date": "2026-08-01", "end_date": "2026-08-31"}
    )
    assert response.data["count"] == 1
    assert response.data["results"][0]["amount"] == "20.00"


@pytest.mark.django_db
def test_transactions_are_paginated(client_a, account_a, food_category):
    for day in range(1, 26):
        Transaction.objects.create(
            user=account_a.user,
            account=account_a,
            category=food_category,
            amount="10.00",
            transaction_type="EXPENSE",
            date=date(2026, 8, day),
        )
    response = client_a.get(TRANSACTIONS_URL)
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20  # PAGE_SIZE
    assert response.data["next"] is not None

    second_page = client_a.get(response.data["next"])
    assert len(second_page.data["results"]) == 5
    assert second_page.data["next"] is None


@pytest.mark.django_db
def test_account_current_balance_reflects_transactions(client_a, account_a, salary_category, food_category):
    client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": salary_category.id,
            "amount": "500.00",
            "transaction_type": "INCOME",
            "date": "2026-08-01",
        },
        format="json",
    )
    client_a.post(
        TRANSACTIONS_URL,
        {
            "account": account_a.id,
            "category": food_category.id,
            "amount": "200.00",
            "transaction_type": "EXPENSE",
            "date": "2026-08-02",
        },
        format="json",
    )
    response = client_a.get(f"/api/v1/accounts/{account_a.id}/")
    # 1000 initial + 500 income - 200 expense = 1300
    assert response.data["current_balance"] == "1300.00"
