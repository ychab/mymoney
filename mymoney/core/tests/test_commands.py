import unittest

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.six import StringIO

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.bankaccounts.models import BankAccount
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactionschedulers.factories import (
    BankTransactionSchedulerFactory,
)
from mymoney.apps.banktransactionschedulers.models import (
    BankTransactionScheduler,
)
from mymoney.apps.banktransactiontags.factories import (
    BankTransactionTagFactory,
)
from mymoney.apps.banktransactiontags.models import BankTransactionTag

from ..factories import UserFactory


class DemoTestCase(unittest.TestCase):

    def test_purge(self):

        user = UserFactory()
        bankaccount = BankAccountFactory()
        tag = BankTransactionTagFactory()
        banktransaction = BankTransactionFactory()
        scheduler = BankTransactionSchedulerFactory()

        out = StringIO()
        call_command('demo', purge=True, interactive=False, stdout=out)
        self.assertEqual(
            out.getvalue(),
            'All data have been deleted.\n',
        )

        user_model = get_user_model()
        with self.assertRaises(user_model.DoesNotExist):
            user_model.objects.get(pk=user.pk)

        with self.assertRaises(BankAccount.DoesNotExist):
            BankAccount.objects.get(pk=bankaccount.pk)

        with self.assertRaises(BankTransactionTag.DoesNotExist):
            BankTransactionTag.objects.get(pk=tag.pk)

        with self.assertRaises(BankTransaction.DoesNotExist):
            BankTransaction.objects.get(pk=banktransaction.pk)

        with self.assertRaises(BankTransactionScheduler.DoesNotExist):
            BankTransactionScheduler.objects.get(pk=scheduler.pk)

    def test_generate(self):

        out = StringIO()
        call_command(
            'demo', username='foo', password='bar', email='foo@bar.com',
            currency='USD', interactive=False, stdout=out,
        )
        self.assertEqual(
            out.getvalue(),
            'Data have been generated successfully.\n',
        )

        user_model = get_user_model()
        user = user_model.objects.get(username='foo')
        self.assertTrue(user.check_password('bar'))
        self.assertEqual(user.email, 'foo@bar.com')
        self.assertEqual(user.user_permissions.count(), 13)

        bankaccount = BankAccount.objects.get(owners=user)
        self.assertEqual(bankaccount.currency, 'USD')

        self.assertEqual(len(BankTransactionTag.objects.filter(owner=user)), 5)
        self.assertEqual(
            (
                BankTransactionScheduler.objects
                .filter(bankaccount=bankaccount)
                .count()
            ),
            3,
        )
        self.assertEqual(
            (
                BankTransaction.objects
                .filter(bankaccount=bankaccount, scheduled=True)
                .count()
            ),
            3,
        )
        self.assertGreaterEqual(
            (
                BankTransaction.objects
                .filter(bankaccount=bankaccount, scheduled=False)
                .count()
            ),
            20,
        )
