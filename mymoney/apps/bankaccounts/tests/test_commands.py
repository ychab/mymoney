import unittest

from django.core.management import call_command
from django.utils.six import StringIO

from ..factories import BankAccountFactory
from ..models import BankAccount


class CommandTestCase(unittest.TestCase):

    def test_command_delete_orphans(self):

        # Create an orphan bank account.
        bankaccount = BankAccountFactory()

        out = StringIO()
        call_command('deleteorphansbankaccounts', stdout=out)

        with self.assertRaises(BankAccount.DoesNotExist):
            bankaccount.refresh_from_db()

        self.assertIn('Bank accounts deleted.', out.getvalue())
