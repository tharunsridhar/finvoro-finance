from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.transactions.models import Transaction


TWO_PLACES = Decimal("0.01")


def _int_param(request, name, default):
    value = request.query_params.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _money(value):
    return str((value or Decimal("0")).quantize(TWO_PLACES))


class SummaryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        month = _int_param(request, "month", today.month)
        year = _int_param(request, "year", today.year)

        accounts = Account.objects.filter(user=request.user)
        total_balance = sum((account.current_balance for account in accounts), Decimal("0"))

        month_totals = Transaction.objects.filter(
            user=request.user, date__year=year, date__month=month
        ).aggregate(
            income=Sum("amount", filter=Q(transaction_type="INCOME")),
            expenses=Sum("amount", filter=Q(transaction_type="EXPENSE")),
        )
        income = month_totals["income"] or Decimal("0")
        expenses = month_totals["expenses"] or Decimal("0")

        recent = Transaction.objects.filter(user=request.user).select_related(
            "account", "category"
        )[:5]
        recent_data = [
            {
                "id": t.id,
                "account": t.account.name,
                "category": t.category.name,
                "amount": _money(t.amount),
                "transaction_type": t.transaction_type,
                "date": t.date,
                "description": t.description,
            }
            for t in recent
        ]

        return Response(
            {
                "month": month,
                "year": year,
                "total_balance": _money(total_balance),
                "monthly_income": _money(income),
                "monthly_expenses": _money(expenses),
                "net_change": _money(income - expenses),
                "recent_transactions": recent_data,
            }
        )


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        year = _int_param(request, "year", today.year)

        rows = (
            Transaction.objects.filter(user=request.user, date__year=year)
            .values("date__month")
            .annotate(
                income=Sum("amount", filter=Q(transaction_type="INCOME")),
                expenses=Sum("amount", filter=Q(transaction_type="EXPENSE")),
            )
            .order_by("date__month")
        )

        results = []
        for row in rows:
            income = row["income"] or Decimal("0")
            expenses = row["expenses"] or Decimal("0")
            results.append(
                {
                    "month": row["date__month"],
                    "income": _money(income),
                    "expenses": _money(expenses),
                    "net_change": _money(income - expenses),
                }
            )

        return Response({"year": year, "results": results})


class CategoryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        month = _int_param(request, "month", today.month)
        year = _int_param(request, "year", today.year)
        transaction_type = request.query_params.get("transaction_type", "EXPENSE").upper()

        rows = (
            Transaction.objects.filter(
                user=request.user,
                date__year=year,
                date__month=month,
                transaction_type=transaction_type,
            )
            .values("category__id", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        results = [
            {
                "category_id": row["category__id"],
                "category_name": row["category__name"],
                "total": _money(row["total"]),
            }
            for row in rows
        ]

        return Response(
            {
                "month": month,
                "year": year,
                "transaction_type": transaction_type,
                "results": results,
            }
        )


class AccountReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(user=request.user)
        results = [
            {
                "account_id": account.id,
                "account_name": account.name,
                "account_type": account.account_type,
                "current_balance": _money(account.current_balance),
            }
            for account in accounts
        ]
        return Response({"results": results})
