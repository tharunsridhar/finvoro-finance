from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.categories.models import Category
from apps.transactions.models import Transaction
from apps.users.models import User

SUMMARY_URL = "/api/v1/reports/summary/"
MONTHLY_URL = "/api/v1/reports/monthly/"
CATEGORIES_URL = "/api/v1/reports/categories/"
ACCOUNTS_URL = "/api/v1/reports/accounts/"


@pytest.fixture
def user_a():
    return User.objects.create_user(email="a@example.com", password="StrongPass123!")


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def account_a(user_a):
    return Account.objects.create(
        user=user_a, name="Bank A", account_type="BANK", initial_balance="1000.00"
    )


@pytest.fixture
def salary_category():
    return Category.objects.get(user__isnull=True, name="Salary")


@pytest.fixture
def food_category():
    return Category.objects.get(user__isnull=True, name="Food")


@pytest.fixture
def seeded_transactions(user_a, account_a, salary_category, food_category):
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=salary_category,
        amount="500.00",
        transaction_type="INCOME",
        date=date(2026, 8, 1),
    )
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=food_category,
        amount="200.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 2),
    )
    Transaction.objects.create(
        user=user_a,
        account=account_a,
        category=food_category,
        amount="50.00",
        transaction_type="EXPENSE",
        date=date(2026, 7, 15),
    )


@pytest.mark.django_db
def test_summary_report(client_a, seeded_transactions):
    response = client_a.get(SUMMARY_URL, {"month": 8, "year": 2026})
    assert response.status_code == 200
    assert response.data["monthly_income"] == "500.00"
    assert response.data["monthly_expenses"] == "200.00"
    assert response.data["net_change"] == "300.00"
    assert response.data["total_balance"] == "1250.00"


@pytest.mark.django_db
def test_monthly_report_groups_by_month(client_a, seeded_transactions):
    response = client_a.get(MONTHLY_URL, {"year": 2026})
    months = {row["month"]: row for row in response.data["results"]}
    assert months[8]["income"] == "500.00"
    assert months[8]["expenses"] == "200.00"
    assert months[7]["expenses"] == "50.00"


@pytest.mark.django_db
def test_category_report(client_a, seeded_transactions):
    response = client_a.get(CATEGORIES_URL, {"month": 8, "year": 2026, "transaction_type": "EXPENSE"})
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["category_name"] == "Food"
    assert results[0]["total"] == "200.00"


@pytest.mark.django_db
def test_account_report(client_a, account_a, seeded_transactions):
    response = client_a.get(ACCOUNTS_URL)
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["account_name"] == "Bank A"


@pytest.mark.django_db
def test_reports_require_authentication():
    client = APIClient()
    for url in (SUMMARY_URL, MONTHLY_URL, CATEGORIES_URL, ACCOUNTS_URL):
        response = client.get(url)
        assert response.status_code == 401


@pytest.mark.django_db
def test_reports_scoped_to_requesting_user(client_a, user_a, account_a, food_category):
    other_user = User.objects.create_user(email="other@example.com", password="StrongPass123!")
    other_account = Account.objects.create(
        user=other_user, name="Other Bank", account_type="BANK", initial_balance="999.00"
    )
    Transaction.objects.create(
        user=other_user,
        account=other_account,
        category=food_category,
        amount="700.00",
        transaction_type="EXPENSE",
        date=date(2026, 8, 3),
    )

    response = client_a.get(SUMMARY_URL, {"month": 8, "year": 2026})
    assert response.data["monthly_expenses"] == "0.00"
