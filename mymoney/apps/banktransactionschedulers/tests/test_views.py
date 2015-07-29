import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase, modify_settings
from django.utils import timezone

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionSchedulerFactory


@modify_settings(MIDDLEWARE_CLASSES={
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
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_create(self):
        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Missing permission.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Having permission but not owner.
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permission.
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank account.
        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': 20120918,
        })
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
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
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank transaction.
        url = reverse('banktransactionschedulers:update', kwargs={
            'pk': 20140923
        })
        self.client.login(username=self.superowner, password='test')
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
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()


class ViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

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

        response = self.app.get(url, user='owner')
        self.assertQuerysetEqual(
            response.context['object_list'],
            [
                repr(bts1),
                repr(bts2),
            ],
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
