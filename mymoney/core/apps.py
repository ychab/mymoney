from django.apps import AppConfig


class MyMoneyConfig(AppConfig):
    name = 'mymoney.core'
    verbose_name = "MyMoney"

    def ready(self):
        import mymoney.core.checks  # noqa
