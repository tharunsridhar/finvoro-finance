from django.conf import settings
from django.db import models


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        "categories.Category", on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0), name="transaction_amount_positive"
            ),
        ]
        indexes = [
            models.Index(fields=["user", "date"], name="txn_user_date_idx"),
            models.Index(fields=["user", "transaction_type"], name="txn_user_type_idx"),
        ]
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.date}"
