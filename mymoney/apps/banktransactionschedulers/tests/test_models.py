import datetime
import unittest
from decimal import Decimal
from unittest.mock import patch

from django.db.models import QuerySet
from django.utils import timezone

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.bankaccounts.models import BankAccount
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactiontags.factories import BankTransactionTagFactory

from ..factories import BankTransactionSchedulerFactory
from ..models import BankTransactionScheduler


class ModelTestCase(unittest.TestCase):

    def test_clone_succeed(self):

        bankaccount = BankAccountFactory(balance=0)

        # Test monthly, with recurrence.
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            amount=Decimal('10.23'),
            date=datetime.date(2015, 1, 31),
            memo="Test",
            reconciled=True,
            status=BankTransaction.STATUS_ACTIVE,
            tag=BankTransactionTagFactory(),
            type=BankTransactionScheduler.TYPE_MONTHLY,
            last_action=None,
            state=BankTransactionScheduler.STATE_WAITING,
            recurrence=2,
        )

        bts.clone()
        bt_clone = BankTransaction.objects.order_by('pk').last()
        self.assertEqual(bt_clone.label, bts.label)
        self.assertEqual(bt_clone.amount, bts.amount)
        self.assertEqual(bt_clone.payment_method, bts.payment_method)
        self.assertEqual(bt_clone.memo, bts.memo)
        self.assertEqual(bt_clone.tag.pk, bts.tag.pk)
        self.assertFalse(bt_clone.reconciled)
        self.assertTrue(bt_clone.scheduled)
        self.assertEqual(bt_clone.status, bts.status)
        self.assertEqual(
            bt_clone.date,
            datetime.date(2015, 2, 28),
        )

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('10.23'))

        self.assertEqual(bts.date, bt_clone.date)
        self.assertIsNotNone(bts    .last_action)
        self.assertEqual(bts.recurrence, 1)
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_FINISHED)

        # Clone it again to delete it.
        bts.clone()
        with self.assertRaises(BankTransactionScheduler.DoesNotExist):
            bts.refresh_from_db()

        # Test weekly, infinity
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            amount=Decimal(-45.74),
            date=datetime.date(2015, 3, 26),
            status=BankTransactionScheduler.STATUS_INACTIVE,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            recurrence=None,
            last_action=timezone.make_aware(datetime.datetime(2015, 1, 31, 10)),
            state=BankTransactionScheduler.STATE_FINISHED,
        )
        bts.clone()

        bt_clone = BankTransaction.objects.order_by('pk').last()
        self.assertEqual(
            bt_clone.date,
            datetime.date(2015, 4, 2),
        )

        # Clone inactive doesn't alter bank account balance.
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('20.46'))

        self.assertEqual(bts.date, datetime.date(2015, 4, 2))
        self.assertNotEqual(
            bts.last_action,
            timezone.make_aware(
                datetime.datetime.strptime(
                    '2015-03-26 03:50:00',
                    '%Y-%m-%d %H:%M:%S',
                )
            )
        )
        self.assertIsNone(bts.recurrence)
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_FINISHED)

        # Clone it again
        bts.clone()
        bts.refresh_from_db()
        self.assertEqual(bts.date, datetime.date(2015, 4, 9))

    @patch.object(BankTransaction, 'save')
    def test_clone_insert_failed(self, save_mock):
        save_mock.side_effect = Exception('Click-click boom!')

        bankaccount = BankAccountFactory(balance=0)
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            recurrence=5,
            date=datetime.date(2015, 7, 10),
            last_action=None,
            state=BankTransactionScheduler.STATE_WAITING,
        )

        with self.assertLogs(logger='mymoney.apps.banktransactionschedulers.models',
                             level='ERROR'):
            bts.clone()

        bts.refresh_from_db()
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_FAILED)
        self.assertEqual(bts.date, datetime.date(2015, 7, 10))
        self.assertEqual(bts.recurrence, 5)
        self.assertIsNone(bts.last_action)

    def test_clone_update_failed(self):

        bankaccount = BankAccountFactory(balance=0)
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            recurrence=2,
            state=BankTransactionScheduler.STATE_WAITING,
            last_action=None,
        )

        with patch.object(BankTransactionScheduler, 'save', side_effect=Exception('Click-click boom!')):
            with self.assertLogs(logger='mymoney.apps.banktransactionschedulers.models',
                                 level='ERROR'):
                bts.clone()

        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=bankaccount).count(),
            0,
        )

        bts.refresh_from_db()
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_FAILED)
        self.assertEqual(bts.recurrence, 2)
        self.assertIsNone(bts.last_action)

    @patch.object(BankTransactionScheduler, 'delete')
    def test_clone_delete_failed(self, delete_mock):
        delete_mock.side_effect = Exception('Click-click boom!')

        bankaccount = BankAccountFactory(balance=0)
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            recurrence=1,
        )

        with self.assertLogs(logger='mymoney.apps.banktransactionschedulers.models',
                             level='ERROR'):
            bts.clone()

        bts.refresh_from_db()
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_FAILED)

    @patch.object(QuerySet, 'update')
    def test_clone_queryset_update_failed(self, update_mock):
        update_mock.side_effect = Exception('Click-click Booom!')

        bankaccount = BankAccountFactory(balance=0)
        bts = BankTransactionSchedulerFactory(
            bankaccount=bankaccount,
            recurrence=None,
            state=BankTransactionScheduler.STATE_WAITING,
            last_action=None,
        )

        with patch.object(BankTransactionScheduler, 'save', side_effect=Exception('Click-click Booom!')):
            with self.assertLogs(logger='mymoney.apps.banktransactionschedulers.models',
                                 level='ERROR'):
                bts.clone()

        bts.refresh_from_db()
        self.assertEqual(bts.state, BankTransactionScheduler.STATE_WAITING)
        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=bankaccount).count(),
            0,
        )


class ManagerTestCase(unittest.TestCase):

    def setUp(self):

        for bankaccount in BankAccount.objects.all():
            bankaccount.delete()

        self.bankaccount = BankAccountFactory(balance=0)

    def tearDown(self):
        self.bankaccount.delete()

    def test_awaiting_bank_transactions(self):

        # Waiting, should be good.
        bts1 = BankTransactionSchedulerFactory(
            amount=Decimal('0'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            state=BankTransactionScheduler.STATE_WAITING,
            last_action=None,
        )

        # Finished, but need to be reroll.
        bts2 = BankTransactionSchedulerFactory(
            amount=Decimal('0'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            state=BankTransactionScheduler.STATE_FINISHED,
            last_action=timezone.make_aware(datetime.datetime(2015, 5, 19, 15)),
        )

        # Finished, but need to be reroll.
        bts3 = BankTransactionSchedulerFactory(
            amount=Decimal('0'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            state=BankTransactionScheduler.STATE_FINISHED,
            last_action=timezone.make_aware(datetime.datetime(2015, 5, 19, 15)),
        )

        # Failed, do nothing.
        bts4 = BankTransactionSchedulerFactory(  # noqa
            amount=Decimal('0'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            state=BankTransactionScheduler.STATE_FAILED,
            last_action=None,
        )

        # Month and week
        with patch('django.utils.timezone.now'):
            timezone.now.return_value = timezone.make_aware(
                datetime.datetime(2015, 6, 2, 15),
            )
            qs = BankTransactionScheduler.objects.get_awaiting_banktransactions()
            qs = qs.order_by('pk')
            self.assertListEqual(
                [obj.pk for obj in qs],
                [bts1.pk, bts2.pk, bts3.pk],
            )

        # Week only.
        with patch('django.utils.timezone.now'):
            timezone.now.return_value = timezone.make_aware(
                datetime.datetime(2015, 5, 26, 15),
            )
            qs = BankTransactionScheduler.objects.get_awaiting_banktransactions()
            qs = qs.order_by('pk')
            self.assertListEqual(
                [obj.pk for obj in qs],
                [bts1.pk, bts3.pk],
            )

        # None of both.
        with patch('django.utils.timezone.now'):
            timezone.now.return_value = timezone.make_aware(
                datetime.datetime(2015, 5, 20),
            )
            qs = BankTransactionScheduler.objects.get_awaiting_banktransactions()
            qs = qs.order_by('pk')
            self.assertListEqual(
                [obj.pk for obj in qs],
                [bts1.pk],
            )

    def test_total_debit(self):

        total = BankTransactionScheduler.objects.get_total_debit(self.bankaccount)
        self.assertFalse(total)

        BankTransactionSchedulerFactory(
            amount=Decimal('-15'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('35'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('-30'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('-5'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
        )
        # Inactive.
        BankTransactionSchedulerFactory(
            amount=Decimal('-5'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            status=BankTransactionScheduler.STATUS_INACTIVE,
        )
        # Not a scheduler, don't count it.
        BankTransactionFactory(
            amount=Decimal('-10'),
            bankaccount=self.bankaccount,
        )

        total = BankTransactionScheduler.objects.get_total_debit(self.bankaccount)
        self.assertDictEqual(total, {
            BankTransactionScheduler.TYPE_MONTHLY: Decimal(-45),
            BankTransactionScheduler.TYPE_WEEKLY: Decimal(-5),
        })

    def test_total_credit(self):

        total = BankTransactionScheduler.objects.get_total_credit(self.bankaccount)
        self.assertFalse(total)

        BankTransactionSchedulerFactory(
            amount=Decimal('15'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('-35'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('30'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
        )
        BankTransactionSchedulerFactory(
            amount=Decimal('5'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
        )
        # Inactive.
        BankTransactionSchedulerFactory(
            amount=Decimal('5'),
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            status=BankTransactionScheduler.STATUS_INACTIVE,
        )
        # Not a scheduler, don't count it.
        BankTransactionFactory(
            amount=Decimal('10'),
            bankaccount=self.bankaccount,
        )

        total = BankTransactionScheduler.objects.get_total_credit(self.bankaccount)
        self.assertDictEqual(total, {
            BankTransactionScheduler.TYPE_MONTHLY: Decimal(45),
            BankTransactionScheduler.TYPE_WEEKLY: Decimal(5),
        })


class RelationshipTestCase(unittest.TestCase):

    def test_delete_bankaccount(self):

        bankaccount = BankAccountFactory()
        BankTransactionSchedulerFactory.create_batch(5)

        bankaccount_pk = bankaccount.pk
        bankaccount.delete()

        self.assertEqual(
            BankTransactionScheduler.objects.filter(bankaccount__pk=bankaccount_pk).count(),
            0,
        )
