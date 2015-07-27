import unittest

from mymoney.core.factories import UserFactory

from ..factories import BankAccountFactory
from ..models import BankAccount


class SignalsTestCase(unittest.TestCase):

    def test_owner_delete_signal(self):

        owner = UserFactory()
        bankaccount = BankAccountFactory(owners=[owner])

        owner.delete()
        with self.assertRaises(BankAccount.DoesNotExist):
            bankaccount.refresh_from_db()
