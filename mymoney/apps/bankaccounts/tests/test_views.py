from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import modify_settings, TestCase

from mymoney.core.factories import UserFactory

from ..factories import BankAccountFactory


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
        url = reverse('bankaccounts:list')

        # Anonymous redirected
        response = self.client.get(url)
        self.assertRedirects(response,
                             reverse(settings.LOGIN_URL) + '?next=' + url)
        # Any authenticated user.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_create(self):
        url = reverse('bankaccounts:create')

        # Missing permission.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Having permission.
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

    def test_access_update(self):
        url = reverse('bankaccounts:update', kwargs={'pk': self.bankaccount.pk})

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

        # Fake bank account.
        url = reverse('bankaccounts:update', kwargs={'pk': 20140923})
        self.client.login(username=self.superowner, password='test')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.logout()

    def test_access_delete(self):
        url = reverse('bankaccounts:delete', kwargs={'pk': self.bankaccount.pk})

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


class ViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_list_view(self):

        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(reverse('bankaccounts:list'))
        ids = list((response.context_data['bankaccount_list']
                    .values_list('pk', flat=True)))
        self.assertFalse(ids)

        bankaccount = BankAccountFactory(
            owners=(self.not_owner, self.owner),
        )

        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(reverse('bankaccounts:list'))
        ids = list((response.context_data['bankaccount_list']
                    .values_list('pk', flat=True)))
        self.assertListEqual([bankaccount.pk], ids)

        self.client.login(username=self.owner, password='test')
        response = self.client.get(reverse('bankaccounts:list'))
        ids = list((response.context_data['bankaccount_list']
                    .values_list('pk', flat=True)))
        self.assertListEqual(
            sorted([self.bankaccount.pk, bankaccount.pk]),
            sorted(ids),
        )
