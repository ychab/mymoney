import datetime
import unittest
from decimal import Decimal
from unittest.mock import patch

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.bankaccounts.models import BankAccount
from mymoney.apps.banktransactiontags.factories import BankTransactionTagFactory

from ..factories import BankTransactionFactory
from ..models import BankTransaction


class ModelTestCase(unittest.TestCase):

    def test_bankaccount_update_fail(self):

        bankaccount = BankAccountFactory(balance=0)

        with patch.object(BankAccount, 'save', side_effect=Exception('Bang')):
            with self.assertRaises(Exception):
                BankTransactionFactory(
                    bankaccount=bankaccount,
                    amount='15.59',
                )

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, 0)

    def test_banktransaction_insert_fail(self):

        bankaccount = BankAccountFactory(balance=0)

        with patch.object(BankTransaction, 'save', side_effect=Exception('Bang')):
            with self.assertRaises(Exception):
                BankTransactionFactory(
                    bankaccount=bankaccount,
                    amount='15.59',
                )

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, 0)

    def test_banktransaction_update_fail(self):

        bankaccount = BankAccountFactory(balance=0)
        banktransaction = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-10',
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(-10))

        with patch.object(BankTransaction, 'save', side_effect=Exception('Bang')):
            with self.assertRaises(Exception):
                banktransaction.amount = -50
                banktransaction.save()

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(-10))

    def test_save_success(self):

        bankaccount = BankAccountFactory(balance=-10)

        # Test insert.
        banktransaction = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='15.59',
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('5.59'))

        # Then test update.
        banktransaction.refresh_from_db()
        banktransaction.amount += Decimal('14.41')
        banktransaction.save()
        bankaccount.refresh_from_db()

        self.assertEqual(bankaccount.balance, Decimal('20'))

    def test_delete(self):

        bankaccount = BankAccountFactory(balance=50)

        banktransaction = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-25',
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(25))

        banktransaction.delete()
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(50))

    def test_status_disabled(self):

        # Test with create op.
        bankaccount = BankAccountFactory(balance=100)

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('150'),
            status=BankTransaction.STATUS_INACTIVE
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal(100))

        # Then test with update.
        banktransaction = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('150'),
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('250'))

        banktransaction.status = BankTransaction.STATUS_INACTIVE
        banktransaction.amount = Decimal('180')
        banktransaction.save()
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('250'))

        # Then test with delete op.
        banktransaction.delete()
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('250'))

    def test_force_currency(self):

        bankaccount = BankAccountFactory(currency='EUR')

        banktransaction = BankTransactionFactory(
            bankaccount=bankaccount,
            currency='USD',
        )
        self.assertEqual(banktransaction.currency, 'EUR')

        banktransaction.currency = 'USD'
        banktransaction.save()
        self.assertEqual(banktransaction.currency, 'EUR')


class ManagerTestCase(unittest.TestCase):

    def test_current_balance(self):

        bankaccount = BankAccountFactory(balance=0)

        self.assertEqual(
            BankTransaction.objects.get_current_balance(bankaccount),
            0,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-15,
            date=datetime.date.today() - datetime.timedelta(5),
        )
        # Ignored for stat only, so used here.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=10,
            date=datetime.date.today() - datetime.timedelta(7),
            status=BankTransaction.STATUS_IGNORED,
        )
        # Next, so not used.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=40,
            date=datetime.date.today() + datetime.timedelta(5),
        )
        # Inactive, don't use it.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=40,
            date=datetime.date.today() - datetime.timedelta(5),
            status=BankTransaction.STATUS_INACTIVE,
        )
        self.assertEqual(
            BankTransaction.objects.get_current_balance(bankaccount),
            Decimal(-5),
        )

        # Try it again with new records.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-30,
            date=datetime.date.today() - datetime.timedelta(5),
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=55,
            date=datetime.date.today() + datetime.timedelta(5),
        )
        self.assertEqual(
            BankTransaction.objects.get_current_balance(bankaccount),
            Decimal(-35),
        )

    def test_reconciled_balance(self):

        bankaccount = BankAccountFactory(balance=0)

        self.assertEqual(
            BankTransaction.objects.get_reconciled_balance(bankaccount),
            0,
        )

        # Not reconciled by default.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-15,
        )
        self.assertEqual(
            BankTransaction.objects.get_reconciled_balance(bankaccount),
            0,
        )

        # Should work.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=40,
            reconciled=True,
        )
        self.assertEqual(
            BankTransaction.objects.get_reconciled_balance(bankaccount),
            Decimal(40),
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-30,
            reconciled=True,
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=55,
        )
        # Inactive, don't use it.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-150,
            reconciled=True,
            status=BankTransaction.STATUS_INACTIVE,
        )
        # Ignored is not inactive, so use it.
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=-5,
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
        )
        self.assertEqual(
            BankTransaction.objects.get_reconciled_balance(bankaccount),
            Decimal(5),
        )


class RelationshipTestCase(unittest.TestCase):

    def test_delete_bankaccount(self):

        bankaccount = BankAccountFactory()
        tag = BankTransactionTagFactory()
        BankTransactionFactory(bankaccount=bankaccount, tag=tag)

        pk = bankaccount.pk
        bankaccount.delete()

        self.assertEqual(
            BankTransaction.objects.filter(bankaccount__pk=pk).count(),
            0,
        )
        # Should not be deleted.
        tag.refresh_from_db()
