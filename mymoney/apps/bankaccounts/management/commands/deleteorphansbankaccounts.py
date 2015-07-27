from django.core.management.base import BaseCommand

from ...models import BankAccount


class Command(BaseCommand):
    """
    Cleanup cron tasks to delete bank accounts which haven't no more owners.
    """
    help = 'Delete orphan bank accounts'

    def handle(self, *args, **options):
        BankAccount.objects.delete_orphans()
        self.stdout.write('Bank accounts deleted.')
