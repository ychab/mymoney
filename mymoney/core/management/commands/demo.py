import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from dateutil.relativedelta import relativedelta
from factory import fuzzy

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.bankaccounts.models import BankAccount
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactionschedulers.factories import BankTransactionSchedulerFactory
from mymoney.apps.banktransactionschedulers.models import BankTransactionScheduler
from mymoney.apps.banktransactiontags.factories import BankTransactionTagFactory
from mymoney.apps.banktransactiontags.models import BankTransactionTag

from ...factories import UserFactory


class Command(BaseCommand):
    """
    Data generator for purpose only.
    """
    help = 'Generate data for purpose.'

    leave_locale_alone = True

    def add_arguments(self, parser):

        parser.add_argument('--username', default='demo', help='Default: demo')
        parser.add_argument('--password', default='demo', help='Default: demo')
        parser.add_argument('--email', default='demo@example.com')
        parser.add_argument('--currency', default='EUR', help='Default : EUR')

        parser.add_argument('--purge', action='store_true', default=False,
                            help="Delete all data relatives to the project's "
                                 "models then exit.")

        parser.add_argument('--noinput', action='store_false',
                            dest='interactive', default=True)

    def handle(self, *args, **options):

        if options.get('purge'):

            if options.get('interactive'):  # pragma: no cover
                msg = "Are you sure to delete all data?"
                choice = input("%s (y/N): " % msg).strip().lower()
                if choice != 'y':
                    return

            # Deleting users only should be enough to delete all instances.
            get_user_model().objects.all().delete()
            BankAccount.objects.all().delete()
            BankTransactionTag.objects.all().delete()
            BankTransaction.objects.all().delete()
            BankTransactionScheduler.objects.all().delete()

            self.stdout.write('All data have been deleted.')
            return

        user = UserFactory(
            username=options.get('username'),
            password=options.get('password'),
            email=options.get('email'),
            user_permissions='admin',
        )

        bankaccount = BankAccountFactory(
            label=_('Current account'),
            balance=2000,
            balance_initial=150,
            currency=options.get('currency'),
            owners=[user],
        )

        tag_rent = BankTransactionTagFactory(name=_('Rent'), owner=user)
        tag_shopping = BankTransactionTagFactory(name=_('Shopping'), owner=user)
        tag_car = BankTransactionTagFactory(name=_('Car'), owner=user)
        tag_tax = BankTransactionTagFactory(name=_('Tax'), owner=user)
        tag_restaurant = BankTransactionTagFactory(name=_('Restaurant'), owner=user)

        today = datetime.date.today()

        BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            label=_("Rent"),
            amount=Decimal("-910"),
            date=datetime.date(today.year, today.month, 10),
            payment_method=BankTransaction.PAYMENT_METHOD_TRANSFER,
            tag=tag_rent,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            recurrence=None,
        ).clone()

        BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            label=_("Council tax"),
            amount=Decimal("-99.89"),
            date=datetime.date(today.year, today.month, 15),
            payment_method=BankTransaction.PAYMENT_METHOD_TRANSFER,
            tag=tag_tax,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            recurrence=10,
        ).clone()

        BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            label=_("Wages"),
            amount=Decimal("2615.78"),
            date=datetime.date(today.year, today.month, 5),
            payment_method=BankTransaction.PAYMENT_METHOD_TRANSFER,
            tag=None,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            recurrence=None,
        ).clone()

        BankTransactionFactory(
            bankaccount=bankaccount,
            label=_("Internal transfer"),
            amount=Decimal("500"),
            date=today - relativedelta(months=1, day=28),
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
            payment_method=BankTransaction.PAYMENT_METHOD_TRANSFER_INTERNAL,
            tag=None,
            memo="Ineed$",
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            label=_("Scratch ticket"),
            amount=Decimal("150"),
            date=today,
            reconciled=False,
            payment_method=BankTransaction.PAYMENT_METHOD_CASH,
            tag=None,
            memo="Hooray!",
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            label=_("New tires"),
            amount=Decimal("-189.59"),
            date=today - relativedelta(days=5),
            reconciled=True,
            payment_method=BankTransaction.PAYMENT_METHOD_CHECK,
            tag=tag_car,
            memo="Love my bike!",
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            label=_("Bad stuff"),
            amount=Decimal("-79.90"),
            date=datetime.date(today.year, today.month, 9),
            reconciled=True,
            payment_method=BankTransaction.PAYMENT_METHOD_CREDIT_CARD,
            tag=tag_shopping,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            label=_("Refund"),
            amount=Decimal("49.59"),
            date=datetime.date(today.year, today.month, 15),
            reconciled=True,
            payment_method=BankTransaction.PAYMENT_METHOD_TRANSFER,
            tag=tag_shopping,
        )

        date_start = today + relativedelta(months=-1, day=15)
        date_end = today + relativedelta(months=1, day=15)
        date = date_start

        while date < date_end:

            if date <= today or date.day % 3 == 0:

                choice = [tag_shopping, tag_restaurant, None, None]
                tag = fuzzy.FuzzyChoice(choice).fuzz()

                BankTransactionFactory(
                    bankaccount=bankaccount,
                    label=tag.name if tag is not None else _('Something'),
                    amount=fuzzy.FuzzyDecimal(-100, -10),
                    date=date,
                    reconciled=date < today - relativedelta(days=-3),
                    status=BankTransaction.STATUS_ACTIVE,
                    tag=tag,
                )

            date += relativedelta(days=1)

        self.stdout.write("Data have been generated successfully.")
