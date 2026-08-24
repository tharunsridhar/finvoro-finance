from django.db.models import Q
from rest_framework import viewsets

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filterset_fields = ["category_type"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()
        user = self.request.user
        if self.action in ("update", "partial_update", "destroy"):
            return Category.objects.filter(user=user)
        return Category.objects.filter(Q(user=user) | Q(user__isnull=True))
