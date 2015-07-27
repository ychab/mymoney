from django.contrib import admin

from .models import BankTransactionTag


class BankTransactionTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    list_display_links = ['name']
    ordering = ['name', 'owner']
    search_fields = ['name']

admin.site.register(BankTransactionTag, BankTransactionTagAdmin)
