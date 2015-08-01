from decimal import Decimal

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.utils.translation import ugettext as _

from django_webtest import WebTest

from mymoney.core.factories import UserFactory

from ..factories import BankAccountFactory
from ..models import BankAccount


class FormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):

        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_default_owners(self):

        form = self.app.get(reverse('bankaccounts:create'), user='superowner').form
        self.assertListEqual(
            sorted(['owner', 'not_owner', 'superowner']),
            sorted([option[2] for option in form['owners'].options])
        )
        self.assertListEqual([str(self.superowner.pk)], form['owners'].value)

    def test_owners_field(self):

        form = self.app.get(reverse('bankaccounts:create'), user='not_owner').form
        self.assertNotIn('owners', form.fields)

        form = self.app.get(reverse('bankaccounts:create'), user='superowner').form
        self.assertIn('owners', form.fields)

    @override_settings(
        LANGUAGE_CODE='en-us',
    )
    def test_create_form(self):

        # Without administer owners.
        form = self.app.get(reverse('bankaccounts:create'), user='not_owner').form
        self.assertNotIn('balance', form.fields)
        self.assertNotIn('owners', form.fields)

        edit = {
            'label': 'test_without_perm',
            'balance_initial': '15.00',
            'currency': 'EUR',
        }
        for name, value in edit.items():
            form[name] = value
        form.submit().maybe_follow()

        bankaccount = BankAccount.objects.get(label=edit['label'])
        self.assertEqual(bankaccount.balance_initial, Decimal(edit['balance_initial']))
        self.assertEqual(bankaccount.currency, edit['currency'])
        self.assertListEqual(
            [self.not_owner.pk],
            [owner.pk for owner in bankaccount.owners.all()]
        )

        # With administer owners.
        form = self.app.get(reverse('bankaccounts:create'), user='superowner').form
        self.assertNotIn('balance', form.fields)

        edit = {
            'label': 'test_with_perm',
            'balance_initial': '-15.00',
            'currency': 'EUR',
            'owners': (self.owner.pk, self.superowner.pk),
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        bankaccount = BankAccount.objects.get(label=edit['label'])
        self.assertEqual(bankaccount.balance_initial, Decimal(edit['balance_initial']))
        self.assertEqual(bankaccount.currency, edit['currency'])
        self.assertListEqual(
            sorted([self.owner.pk, self.superowner.pk]),
            sorted([owner.pk for owner in bankaccount.owners.all()])
        )

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank account %(label)s was created successfully' % {
                'label': bankaccount.label
            },
            [message.message for message in storage],
        )

    @override_settings(
        LANGUAGE_CODE='en-us',
    )
    def test_update_form(self):

        # Without administer owners.
        bankaccount = BankAccountFactory(
            balance=Decimal('-10'),
            balance_initial=Decimal('10'),
            currency='EUR',
            owners=(self.not_owner, self.superowner),
        )
        url = reverse('bankaccounts:update', kwargs={'pk': bankaccount.pk})

        form = self.app.get(url, user='not_owner').form
        self.assertNotIn('owners', form.fields)
        edit = {
            'label': 'rename it',
            'balance': '-150.59',
            'balance_initial': '0.00',
            'currency': 'USD',
        }
        for name, value in edit.items():
            form[name] = value
        form.submit().maybe_follow()

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.label, edit['label'])
        self.assertEqual(bankaccount.balance, Decimal(edit['balance']) - 10)
        self.assertEqual(bankaccount.balance_initial, Decimal(edit['balance_initial']))
        self.assertEqual(bankaccount.currency, edit['currency'])
        self.assertListEqual(
            sorted([self.not_owner.pk, self.superowner.pk]),
            sorted([owner.pk for owner in bankaccount.owners.all()])
        )

        # With administer owners.
        form = self.app.get(url, user='superowner').form
        self.assertIn('owners', form.fields)
        edit = {
            'label': 'rename it again',
            'balance': '1750.23',
            'balance_initial': '150',
            'currency': 'EUR',
            'owners': (self.owner.pk, self.superowner.pk),
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.label, edit['label'])
        self.assertEqual(bankaccount.balance, Decimal(edit['balance']) + 150)
        self.assertEqual(bankaccount.balance_initial, Decimal(edit['balance_initial']))
        self.assertEqual(bankaccount.currency, edit['currency'])
        self.assertListEqual(
            sorted([self.owner.pk, self.superowner.pk]),
            sorted([owner.pk for owner in bankaccount.owners.all()])
        )

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank account %(label)s was updated successfully' % {
                'label': bankaccount.label
            },
            [message.message for message in storage],
        )

    def test_delete_form(self):

        bankaccount = BankAccountFactory(owners=(self.superowner,))
        url = reverse('bankaccounts:delete', kwargs={'pk': bankaccount.pk})

        response = self.app.get(url, user='superowner')
        response = response.click(description=_('Cancel'))
        self.assertEqual(
            response.request.path,
            reverse('banktransactions:list', kwargs={
                'bankaccount_pk': bankaccount.pk,
            }),
        )
        bankaccount.refresh_from_db()

        response = (self.app.get(url, user='superowner')
                    .form.submit()
                    .maybe_follow())
        self.assertEqual(response.request.path, reverse('bankaccounts:list'))
        with self.assertRaises(BankAccount.DoesNotExist):
            bankaccount.refresh_from_db()
