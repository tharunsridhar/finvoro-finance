from rest_framework import viewsets

from .filters import BudgetFilter
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    filterset_class = BudgetFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Budget.objects.none()
        return Budget.objects.filter(user=self.request.user).select_related("category")
