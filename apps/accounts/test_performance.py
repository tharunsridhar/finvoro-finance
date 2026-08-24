from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.transactions.models import Transaction
from apps.users.models import User

from .models import Account

ACCOUNTS_URL = "/api/v1/accounts/"


@pytest.fixture
def user_a():
    return User.objects.create_user(email="perf@example.com", password="StrongPass123!")


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


def _make_accounts_with_transactions(user, count):
    food = Category.objects.get(user__isnull=True, name="Food")
    for i in range(count):
        account = Account.objects.create(
            user=user, name=f"Account {i}", account_type="BANK", initial_balance="100.00"
        )
        Transaction.objects.create(
            user=user,
            account=account,
            category=food,
            amount="10.00",
            transaction_type="EXPENSE",
            date=date(2026, 8, 1),
        )


@pytest.mark.django_db
def test_account_list_query_count_does_not_scale_with_account_count(
    client_a, user_a, django_assert_max_num_queries
):
    """
    Regression guard for the N+1 flagged in Phase 5: current_balance used to run
    one extra aggregate query per account. With annotation-based balance
    calculation, the query count must stay flat no matter how many accounts exist.
    """
    _make_accounts_with_transactions(user_a, 10)

    with django_assert_max_num_queries(5):
        response = client_a.get(ACCOUNTS_URL)
        assert response.status_code == 200
        assert response.data["count"] == 10


@pytest.mark.django_db
def test_account_current_balance_correct_with_annotation(client_a, user_a):
    _make_accounts_with_transactions(user_a, 3)
    response = client_a.get(ACCOUNTS_URL)
    for result in response.data["results"]:
        # 100.00 initial - 10.00 expense = 90.00
        assert result["current_balance"] == "90.00"
