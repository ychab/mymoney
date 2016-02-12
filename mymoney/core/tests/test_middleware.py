from django.conf import settings
from django.core.urlresolvers import get_script_prefix, reverse
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

    def test_anonymous_redirect(self):
        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })
        login_url = resolve_url(settings.LOGIN_URL)
        admin_base_url = get_script_prefix() + settings.MYMONEY['ADMIN_BASE_URL']

        # Anonymous should be redirect to login url.
        response = self.client.get(url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)
        self.assertEqual(
            urlunquote(response.request['QUERY_STRING']),
            'next=' + url
        )

        # Check explicit infinite loop with anonymous.
        response = self.client.get(login_url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)

        # However, check that anonymous could access back-office
        response = self.client.get(admin_base_url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], admin_base_url + '/login/')

        # Authentificated user are not redirected.
        self.client.force_login(self.owner)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], url)

        # Check explicit infinite loop after log out.
        logout_url = resolve_url(settings.LOGOUT_URL)
        response = self.client.get(logout_url, follow=True)
        self.assertEqual(response.request['PATH_INFO'], login_url)
