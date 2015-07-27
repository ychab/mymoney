from django.core.urlresolvers import reverse
from django.test import TestCase

from mymoney.apps.bankaccounts.factories import BankAccountFactory

from ..factories import UserFactory


class ContextProcessorsTestCase(TestCase):

    def test_extra(self):

        user = UserFactory(username='superowner', user_permissions='admin')
        bankaccount = BankAccountFactory(owners=[user])
        BankAccountFactory()

        response = self.client.get(reverse('home'), follow=True)
        self.assertNotIn('user_bankaccounts', response.context[0])

        self.client.login(username='superowner', password='test')
        response = self.client.get(reverse('home'), follow=True)
        self.assertListEqual(
            [ba.pk for ba in response.context[0]['user_bankaccounts']],
            [bankaccount.pk],
        )
