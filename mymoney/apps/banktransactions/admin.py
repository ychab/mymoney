from django.contrib import admin

from .models import BankTransaction


class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['label', 'bankaccount', 'date', 'status', 'amount',
                    'reconciled', 'scheduled', 'payment_method']
    list_display_links = ['label']
    list_filter = ['date', 'status', 'reconciled']
    ordering = ['-date']
    date_hierarchy = 'date'
    search_fields = ['label']


admin.site.register(BankTransaction, BankTransactionAdmin)
