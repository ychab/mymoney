from django.core.management.base import BaseCommand

from ...models import BankTransactionScheduler


class Command(BaseCommand):
    help = 'Clone bank transaction scheduled'

    def add_arguments(self, parser):

        parser.add_argument('--limit', action='store', type=int, default=100,
                            help='Limit the number of scheduled bank '
                                 'transaction to clone.')

    def handle(self, *args, **options):

        # Sort by date instead of last action because last action could be NULL
        # and postgreSQL sort NULL value as latest.
        qs = (BankTransactionScheduler.objects
              .get_awaiting_banktransactions()
              .order_by('date')
              [:options['limit']])

        for bts in qs:
            bts.clone()

        self.stdout.write('Scheduled bank transaction have been cloned.')
