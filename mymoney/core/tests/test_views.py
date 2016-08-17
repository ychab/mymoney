from django.urls import reverse
from django.test import TestCase, modify_settings

from mymoney.apps.bankaccounts.factories import BankAccountFactory

from ..factories import UserFactory


@modify_settings(MIDDLEWARE_CLASSES={
    'remove': ['mymoney.core.middleware.AnonymousRedirectMiddleware'],
})
class HomeRedirectViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('home')

    def test_redirect_anonymous(self):

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.resolver_match.view_name, 'login')

    def test_redirect_authenticated_one_bankaccount(self):

        user = UserFactory()
        bankaccount = BankAccountFactory(owners=[user])

        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.resolver_match.view_name, 'banktransactions:list')
        self.assertDictEqual(response.resolver_match.kwargs, {
            'bankaccount_pk': str(bankaccount.pk),
        })

    def test_redirect_authenticated_multiple_bankaccounts(self):

        user = UserFactory()
        BankAccountFactory(owners=[user])
        BankAccountFactory(owners=[user])

        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.resolver_match.view_name, 'bankaccounts:list')
