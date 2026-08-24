from rest_framework import serializers


class RecentTransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    account = serializers.CharField()
    category = serializers.CharField()
    amount = serializers.CharField()
    transaction_type = serializers.CharField()
    date = serializers.DateField()
    description = serializers.CharField()


class SummaryReportSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    total_balance = serializers.CharField()
    monthly_income = serializers.CharField()
    monthly_expenses = serializers.CharField()
    net_change = serializers.CharField()
    recent_transactions = RecentTransactionSerializer(many=True)


class MonthlyReportRowSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    income = serializers.CharField()
    expenses = serializers.CharField()
    net_change = serializers.CharField()


class MonthlyReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    results = MonthlyReportRowSerializer(many=True)


class CategoryReportRowSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    total = serializers.CharField()


class CategoryReportSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    transaction_type = serializers.CharField()
    results = CategoryReportRowSerializer(many=True)


class AccountReportRowSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    account_name = serializers.CharField()
    account_type = serializers.CharField()
    current_balance = serializers.CharField()


class AccountReportSerializer(serializers.Serializer):
    results = AccountReportRowSerializer(many=True)
