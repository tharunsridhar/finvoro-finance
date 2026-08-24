from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import DecimalField, F, Q, Sum
from django.db.models.functions import Coalesce


class AccountQuerySet(models.QuerySet):
    def with_balance(self):
        """Annotate current_balance via a single query per call, instead of one
        aggregate query per account (see apps/accounts/test_performance.py)."""
        money = DecimalField(max_digits=12, decimal_places=2)
        return self.annotate(
            income_total=Coalesce(
                Sum("transactions__amount", filter=Q(transactions__transaction_type="INCOME")),
                Decimal("0"),
                output_field=money,
            ),
            expense_total=Coalesce(
                Sum("transactions__amount", filter=Q(transactions__transaction_type="EXPENSE")),
                Decimal("0"),
                output_field=money,
            ),
        ).annotate(
            balance_annotation=F("initial_balance") + F("income_total") - F("expense_total")
        ).order_by("-created_at")


class Account(models.Model):
    class AccountType(models.TextChoices):
        BANK = "BANK", "Bank"
        CASH = "CASH", "Cash"
        WALLET = "WALLET", "Wallet"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_account_name_per_user"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    @property
    def current_balance(self):
        """Convenience for a single instance not fetched via with_balance()
        (e.g. admin, shell, or a freshly created instance)."""
        annotated = getattr(self, "balance_annotation", None)
        if annotated is not None:
            return annotated
        totals = self.transactions.aggregate(
            income=Sum("amount", filter=Q(transaction_type="INCOME")),
            expense=Sum("amount", filter=Q(transaction_type="EXPENSE")),
        )
        income = totals["income"] or Decimal("0")
        expense = totals["expense"] or Decimal("0")
        return self.initial_balance + income - expense
