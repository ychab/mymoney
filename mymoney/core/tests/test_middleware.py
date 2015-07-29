from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.test import TestCase
from django.utils.http import urlunquote

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.core.factories import UserFactory


class AnonymousRedirectMiddlewareTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])

    def test_(self):
        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })
        login_url = resolve_url(settings.LOGIN_URL)

        response = self.client.get(url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)
        self.assertEqual(
            urlunquote(response.request['QUERY_STRING']),
            'next=' + url
        )

        # Check explicit infinite loop.
        response = self.client.get(login_url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)

        self.client.login(username=self.owner, password='test')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], url)

        # Check explicit infinite loop.
        logout_url = resolve_url(settings.LOGOUT_URL)
        response = self.client.get(logout_url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)
