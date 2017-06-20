import datetime
from decimal import Decimal
from unittest import mock

from django.test import TestCase, modify_settings, override_settings
from django.urls import reverse
from django.utils import timezone

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactionschedulers.models import (
    BankTransactionScheduler,
)
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionSchedulerFactory


@modify_settings(MIDDLEWARE={
    'remove': ['mymoney.core.middleware.AnonymousRedirectMiddleware'],
})
class AccessTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_access_list(self):
        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_create(self):
        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Missing permission.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Having permission but not owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permission.
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank account.
        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': 20120918,
        })
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.logout()

    def test_access_update(self):

        banktransactionscheduler = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
        )

        url = reverse('banktransactionschedulers:update', kwargs={
            'pk': banktransactionscheduler.pk
        })

        # Anonymous
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non-owner with permissions.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank transaction.
        url = reverse('banktransactionschedulers:update', kwargs={
            'pk': 20140923
        })
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.logout()

    def test_access_delete(self):

        banktransactionscheduler = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
        )

        url = reverse('banktransactionschedulers:delete', kwargs={
            'pk': banktransactionscheduler.pk
        })

        # Anonymous
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non-owner with permissions.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()


class ViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')

    def setUp(self):
        self.bankaccount = BankAccountFactory(owners=[self.owner, self.superowner])

    @mock.patch('mymoney.apps.banktransactions.models.timezone')
    @mock.patch('mymoney.apps.banktransactionschedulers.models.timezone')
    def test_summary_queryset(self, mock_bt_timezone, mock_bts_timezone):
        mock_bt_timezone.now.return_value = datetime.date(2015, 8, 11)
        mock_bts_timezone.now.return_value = datetime.date(2015, 8, 11)

        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        self.client.force_login(self.owner)

        # Nothing.
        response = self.client.get(url)
        self.assertFalse(response.context[0]['summary'])
        self.assertEqual(response.context[0]['total'], 0)

        # Only credit.
        bts1 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            amount=Decimal('2000'),
            date=datetime.date(2015, 8, 10),
        )
        response = self.client.get(url)
        self.assertDictEqual(
            response.context[0]['summary'],
            {
                BankTransactionScheduler.TYPE_MONTHLY: {
                    'type': BankTransactionScheduler.TYPES[0][1],
                    'credit': bts1.amount,
                    'debit': 0,
                    'used': 0,
                    'remaining': bts1.amount,
                    'total': bts1.amount,
                },
            },
        )
        self.assertEqual(response.context[0]['total'], bts1.amount)

        # Add debit.
        bts2 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            amount=Decimal('-900'),
            date=datetime.date(2015, 8, 9),
        )
        bts3 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            amount=Decimal('-100'),
            date=datetime.date(2015, 8, 25),
        )
        response = self.client.get(url)
        self.assertDictEqual(
            response.context[0]['summary'],
            {
                BankTransactionScheduler.TYPE_MONTHLY: {
                    'type': BankTransactionScheduler.TYPES[0][1],
                    'credit': bts1.amount,
                    'debit': bts2.amount + bts3.amount,  # -1000
                    'used': 0,
                    'remaining': bts1.amount + bts2.amount + bts3.amount,  # 1000
                    'total': bts1.amount + bts2.amount + bts3.amount,  # 1000
                },
            },
        )
        self.assertEqual(response.context[0]['total'], bts1.amount + bts2.amount + bts3.amount)

        # Add weekly schedulers.
        bts4 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            amount=Decimal('-30'),
            date=datetime.date(2015, 8, 11),
        )
        bts5 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            amount=Decimal('-15'),
            date=datetime.date(2015, 8, 12),
        )
        response = self.client.get(url)
        self.assertDictEqual(
            response.context[0]['summary'][BankTransactionScheduler.TYPE_MONTHLY],
            {
                'type': BankTransactionScheduler.TYPES[0][1],
                'credit': bts1.amount,  # 2000
                'debit': bts2.amount + bts3.amount,  # -1000
                'used': 0,
                'remaining': bts1.amount + bts2.amount + bts3.amount,  # 1000
                'total': bts1.amount + bts2.amount + bts3.amount,  # 1000
            },
        )
        self.assertDictEqual(
            response.context[0]['summary'][BankTransactionScheduler.TYPE_WEEKLY],
            {
                'type': BankTransactionScheduler.TYPES[1][1],
                'credit': 0,
                'debit': bts4.amount + bts5.amount,  # -45
                'used': 0,
                'remaining': bts4.amount + bts5.amount,  # -45
                'total': bts4.amount + bts5.amount,  # -45
            },
        )
        self.assertEqual(
            response.context[0]['total'],
            bts1.amount + bts2.amount + bts3.amount + bts4.amount + bts5.amount
        )

        # Then add bank transactions.
        bt1 = BankTransactionFactory(
            bankaccount=self.bankaccount,
            date=datetime.date(2015, 8, 10),
            amount=Decimal('-150'),
        )
        bt2 = BankTransactionFactory(
            bankaccount=self.bankaccount,
            date=datetime.date(2015, 8, 20),
            amount=Decimal('-50'),
        )
        response = self.client.get(url)
        self.assertDictEqual(
            response.context[0]['summary'][BankTransactionScheduler.TYPE_MONTHLY],
            {
                'type': BankTransactionScheduler.TYPES[0][1],
                'credit': bts1.amount,  # 2000
                'debit': bts2.amount + bts3.amount,  # -1000
                'used': bt1.amount + bt2.amount,  # -200
                'remaining': bts1.amount + bts2.amount + bts3.amount + bt1.amount + bt2.amount,  # 800
                'total': bts1.amount + bts2.amount + bts3.amount,  # 1000
            },
        )
        self.assertDictEqual(
            response.context[0]['summary'][BankTransactionScheduler.TYPE_WEEKLY],
            {
                'type': BankTransactionScheduler.TYPES[1][1],
                'credit': 0,
                'debit': bts4.amount + bts5.amount,  # -45
                'used': bt1.amount,  # -150
                'remaining': bts4.amount + bts5.amount + bt1.amount,  # -195
                'total': bts4.amount + bts5.amount,  # -45
            },
        )
        self.assertEqual(
            response.context[0]['total'],
            bts1.amount + bts2.amount + bts3.amount + bts4.amount + bts5.amount
        )

    def test_list_queryset(self):

        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        bts1 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            last_action=timezone.make_aware(datetime.datetime(2015, 7, 10)),
        )
        bts2 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            last_action=timezone.make_aware(datetime.datetime(2015, 7, 9)),
        )

        # Scheduler of another bank account.
        BankTransactionSchedulerFactory()

        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [
                repr(bts1),
                repr(bts2),
            ],
        )


class WebViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')

    def setUp(self):
        self.bankaccount = BankAccountFactory(owners=[self.owner, self.superowner])

    @override_settings(LANGUAGE_CODE='en-us')
    def test_summary_view(self):

        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # No scheduler yet.
        response = self.app.get(url, user='owner')
        self.assertContains(response, "No scheduled bank transaction yet.")

        # Schedulers of only one type (no global total display).
        bts1 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            amount=Decimal('2000'),
        )
        response = self.app.get(url, user='owner')
        self.assertNotContains(
            response,
            '<tr data-summary-total="{total}">'.format(total=bts1.amount),
        )

        # Schedulers of both types, display a global total.
        bts2 = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            type=BankTransactionScheduler.TYPE_WEEKLY,
            amount=Decimal('-100'),
        )
        response = self.app.get(url, user='owner')
        self.assertContains(
            response,
            '<td data-summary-total="{total:.2f}">'.format(total=bts1.amount + bts2.amount),
        )

    def test_list_links_action(self):

        bts = BankTransactionSchedulerFactory(bankaccount=self.bankaccount)

        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        edit_url = reverse('banktransactionschedulers:update', kwargs={
            'pk': bts.pk
        })
        delete_url = reverse('banktransactionschedulers:delete', kwargs={
            'pk': bts.pk
        })

        response = self.app.get(url, user='superowner')
        response.click(href=edit_url)

        response = self.app.get(url, user='superowner')
        response.click(href=delete_url)

        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=edit_url)

        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=delete_url)
