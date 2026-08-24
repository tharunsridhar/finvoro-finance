from django.db.models import Q
from rest_framework import viewsets

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        user = self.request.user
        if self.action in ("update", "partial_update", "destroy"):
            return Category.objects.filter(user=user)
        return Category.objects.filter(Q(user=user) | Q(user__isnull=True))
