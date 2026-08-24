from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "account_type", "initial_balance", "created_at"]
    list_filter = ["account_type"]
    search_fields = ["name", "user__email"]
