from django.conf import settings
from django.db import models


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
        help_text="Null means this is a system default category shared by all users.",
    )
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CategoryType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "category_type"],
                name="unique_category_per_user",
            ),
            models.UniqueConstraint(
                fields=["name", "category_type"],
                condition=models.Q(user__isnull=True),
                name="unique_default_category",
            ),
        ]
        ordering = ["name"]
        verbose_name_plural = "categories"

    @property
    def is_default(self):
        return self.user_id is None

    def __str__(self):
        return f"{self.name} ({self.category_type})"
