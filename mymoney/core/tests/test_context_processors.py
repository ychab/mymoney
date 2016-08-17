from django.conf import settings
from django.urls import reverse
from django.test import TestCase

from mymoney.apps.bankaccounts.factories import BankAccountFactory

from ..factories import UserFactory


class ContextProcessorsTestCase(TestCase):

    def test_extra(self):

        user = UserFactory(user_permissions='admin')
        bankaccount = BankAccountFactory(owners=[user])
        BankAccountFactory()

        response = self.client.get(reverse('home'), follow=True)
        self.assertNotIn('user_bankaccounts', response.context[0])

        self.client.force_login(user)
        response = self.client.get(reverse('home'), follow=True)
        self.assertListEqual(
            [ba.pk for ba in response.context[0]['user_bankaccounts']],
            [bankaccount.pk],
        )

        mymoney_settings = settings.MYMONEY.copy()
        mymoney_settings['USE_L10N_DIST'] = False
        with self.settings(MYMONEY=mymoney_settings, LANGUAGE_CODE='en-us'):
            response = self.client.get(reverse('home'), follow=True)
            self.assertNotIn('.min.en-US.js', response.context[0]['dist_js_src'])

        mymoney_settings = settings.MYMONEY.copy()
        mymoney_settings['USE_L10N_DIST'] = True
        with self.settings(MYMONEY=mymoney_settings, LANGUAGE_CODE='en-us'):
            response = self.client.get(reverse('home'), follow=True)
            self.assertIn('.min.en-US.js', response.context[0]['dist_js_src'])

        mymoney_settings = settings.MYMONEY.copy()
        mymoney_settings['USE_L10N_DIST'] = True
        with self.settings(MYMONEY=mymoney_settings, LANGUAGE_CODE='fr-fr'):
            response = self.client.get(reverse('home'), follow=True)
            self.assertIn('.min.fr-FR.js', response.context[0]['dist_js_src'])
