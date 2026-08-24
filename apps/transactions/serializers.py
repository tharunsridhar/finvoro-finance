from django.db.models import Q
from rest_framework import serializers

from apps.accounts.models import Account
from apps.categories.models import Category

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    account_name = serializers.CharField(source="account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "account",
            "account_name",
            "category",
            "category_name",
            "amount",
            "transaction_type",
            "date",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            self.fields["account"].queryset = Account.objects.filter(user=request.user)
            self.fields["category"].queryset = Category.objects.filter(
                Q(user=request.user) | Q(user__isnull=True)
            )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        transaction_type = attrs.get(
            "transaction_type", getattr(self.instance, "transaction_type", None)
        )
        category = attrs.get("category", getattr(self.instance, "category", None))

        if category is not None and transaction_type is not None:
            if category.category_type != transaction_type:
                raise serializers.ValidationError(
                    {
                        "category": (
                            f"Category '{category.name}' is a {category.category_type} "
                            f"category and cannot be used for a {transaction_type} transaction."
                        )
                    }
                )
        return attrs
