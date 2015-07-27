from django.apps import AppConfig


class BankAccountConfig(AppConfig):
    name = 'mymoney.apps.bankaccounts'
    verbose_name = "Bank accounts"

    def ready(self):
        import mymoney.apps.bankaccounts.signals.handlers  # noqa
