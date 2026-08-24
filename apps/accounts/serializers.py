from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "name",
            "account_type",
            "initial_balance",
            "current_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Account.objects.all(),
                fields=["user", "name"],
                message="You already have an account with this name.",
            )
        ]

    def validate_initial_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Initial balance cannot be negative.")
        return value
