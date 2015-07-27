import datetime
import unittest
from decimal import Decimal

from django.core.management import call_command
from django.utils import timezone
from django.utils.six import StringIO

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.models import BankTransaction

from ..factories import BankTransactionSchedulerFactory
from ..models import BankTransactionScheduler


class CommandTestCase(unittest.TestCase):

    def test_scheduler(self):

        bankaccount = BankAccountFactory(balance=0)

        BankTransactionSchedulerFactory(
            amount=Decimal(10),
            bankaccount=bankaccount,
            date="2015-01-31",
            last_action=None,
            state=BankTransactionScheduler.STATE_WAITING,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal(20),
            bankaccount=bankaccount,
            date="2015-01-31",
            type="monthly",
            recurrence="2",
            last_action=None,
            state=BankTransactionScheduler.STATE_WAITING,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal(-5),
            bankaccount=bankaccount,
            date="2015-03-26",
            status=BankTransactionScheduler.STATUS_INACTIVE,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            recurrence=None,
            last_action=timezone.make_aware(datetime.datetime(2015, 1, 31, 10)),
            state=BankTransactionScheduler.STATE_FINISHED,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal(10),
            bankaccount=bankaccount,
            date="2015-01-31",
            last_action=timezone.now() + datetime.timedelta(days=100),
            state=BankTransactionScheduler.STATE_FINISHED,
        )

        # Clone two first scheduled.
        out = StringIO()
        call_command('clonescheduled', limit=2, stdout=out)
        self.assertIn('Scheduled bank transaction have been cloned.', out.getvalue())
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(30))
        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=bankaccount).count(),
            2,
        )

        # Clone latest.
        call_command('clonescheduled', stdout=StringIO())
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(30))
        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=bankaccount).count(),
            3,
        )

        # Nothing happen.
        call_command('clonescheduled', stdout=StringIO())
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(30))
        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=bankaccount).count(),
            3,
        )
