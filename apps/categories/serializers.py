from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_default = serializers.BooleanField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "user", "name", "category_type", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["user", "name", "category_type"],
                message="You already have a category with this name and type.",
            )
        ]
