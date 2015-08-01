import unittest
from decimal import Decimal

from ..factories import BankAccountFactory


class BankAccountSaveTestCase(unittest.TestCase):

    def test_balance_initial_insert(self):

        bankaccount = BankAccountFactory(
            balance=Decimal('0'), balance_initial=Decimal('0'),
        )
        self.assertEqual(bankaccount.balance, Decimal('0'))

        bankaccount = BankAccountFactory(
            balance=Decimal('0'), balance_initial=Decimal('10'),
        )
        self.assertEqual(bankaccount.balance, Decimal('10'))

        bankaccount = BankAccountFactory(
            balance=Decimal('0'), balance_initial=Decimal('-10'),
        )
        self.assertEqual(bankaccount.balance, Decimal('-10'))

        bankaccount = BankAccountFactory(
            balance=Decimal('10'), balance_initial=Decimal('-10'),
        )
        self.assertEqual(bankaccount.balance, Decimal('0'))

        bankaccount = BankAccountFactory(
            balance=Decimal('10'), balance_initial=Decimal('10'),
        )
        self.assertEqual(bankaccount.balance, Decimal('20'))

    def test_balance_initial_update(self):

        bankaccount = BankAccountFactory(
            balance=Decimal('0'), balance_initial=Decimal('0'),
        )

        bankaccount.balance = Decimal('10')
        bankaccount.balance_initial = Decimal('10')
        bankaccount.save()
        self.assertEqual(bankaccount.balance, Decimal('20'))

        bankaccount.balance_initial = Decimal('-20')
        bankaccount.save()
        self.assertEqual(bankaccount.balance, Decimal('-10'))
