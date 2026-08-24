from decimal import Decimal

from django.db.models import Q, Sum
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.categories.models import Category
from apps.transactions.models import Transaction

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_name = serializers.CharField(source="category.name", read_only=True)
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "user",
            "category",
            "category_name",
            "amount",
            "month",
            "year",
            "spent",
            "remaining",
            "percentage_used",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Budget.objects.all(),
                fields=["user", "category", "month", "year"],
                message="A budget for this category and month already exists.",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            self.fields["category"].queryset = Category.objects.filter(
                Q(user=request.user) | Q(user__isnull=True), category_type="EXPENSE"
            )

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value

    def _spent(self, obj):
        if not hasattr(obj, "_spent_cache"):
            total = Transaction.objects.filter(
                user=obj.user,
                category=obj.category,
                transaction_type="EXPENSE",
                date__year=obj.year,
                date__month=obj.month,
            ).aggregate(total=Sum("amount"))["total"]
            obj._spent_cache = total or Decimal("0")
        return obj._spent_cache

    def get_spent(self, obj) -> str:
        return str(self._spent(obj).quantize(Decimal("0.01")))

    def get_remaining(self, obj) -> str:
        remaining = obj.amount - self._spent(obj)
        return str(remaining.quantize(Decimal("0.01")))

    def get_percentage_used(self, obj) -> float:
        spent = self._spent(obj)
        if obj.amount == 0:
            return 0.0
        return round(float(spent / obj.amount * 100), 2)
