from django.urls import path

from .views import AccountReportView, CategoryReportView, MonthlyReportView, SummaryReportView

urlpatterns = [
    path("summary/", SummaryReportView.as_view(), name="report-summary"),
    path("monthly/", MonthlyReportView.as_view(), name="report-monthly"),
    path("categories/", CategoryReportView.as_view(), name="report-categories"),
    path("accounts/", AccountReportView.as_view(), name="report-accounts"),
]
