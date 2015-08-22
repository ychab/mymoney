from decimal import Decimal

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.utils.translation import ugettext as _

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactiontags.factories import \
    BankTransactionTagFactory
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionFactory
from ..models import BankTransaction


class FormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')

    def setUp(self):
        self.bankaccount = BankAccountFactory(balance=0, owners=[self.superowner])

    def test_default_bankaccount(self):

        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='superowner').form
        self.assertNotIn('bankaccount', form.fields)

        edit = {
            'label': 'test implicit bank account',
            'amount': '0.00',
        }
        for name, value in edit.items():
            form[name] = value
        form.submit().maybe_follow()

        banktransaction = BankTransaction.objects.get(label=edit['label'])
        self.assertEqual(banktransaction.bankaccount.pk, self.bankaccount.pk)

        url = reverse('banktransactions:update', kwargs={
            'pk': banktransaction.pk
        })

        form = self.app.get(url, user='superowner').form
        self.assertNotIn('bankaccount', form.fields)

        edit = {
            'label': 'new label',
            'amount': '-10.00',
        }
        for name, value in edit.items():
            form[name] = value
        form.submit().maybe_follow()

        banktransaction.refresh_from_db()
        self.assertEqual(banktransaction.bankaccount.pk, self.bankaccount.pk)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_field_tag(self):

        tag1 = BankTransactionTagFactory(owner=self.superowner)
        tag2 = BankTransactionTagFactory(owner=self.superowner)
        tag3 = BankTransactionTagFactory(owner=self.superowner)
        tag4 = BankTransactionTagFactory()

        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='superowner').form

        # Check available options.
        self.assertListEqual(
            sorted([option[0] for option in form['tag'].options]),
            ['', str(tag1.pk), str(tag2.pk), str(tag3.pk)]
        )

        # Test with a fake tag.
        edit = {
            'label': 'test fake tags',
            'amount': '-154.12',
        }
        for name, value in edit.items():
            form[name] = value
        form['tag'].force_value(['-1'])

        response = form.submit().maybe_follow()
        self.assertFormError(
            response,
            'form',
            'tag',
            [
                'Select a valid choice. That choice is not one of the '
                'available choices.'
            ]
        )
        with self.assertRaises(BankTransaction.DoesNotExist):
            BankTransaction.objects.get(label=edit['label'])

        # Test with with a non-owner tag.
        banktransaction = BankTransactionFactory(bankaccount=self.bankaccount)
        form = self.app.get(
            reverse('banktransactions:update', kwargs={
                'pk': banktransaction.pk
            }),
            user='superowner'
        ).form

        edit = {
            'label': 'test wrong tags',
            'amount': '-45.21',
        }
        for name, value in edit.items():
            form[name] = value
        form['tag'].force_value([str(tag4.pk)])
        response = form.submit().maybe_follow()
        self.assertFormError(
            response,
            'form',
            'tag',
            [
                'Select a valid choice. That choice is not one of the '
                'available choices.'
            ]
        )
        with self.assertRaises(BankTransaction.DoesNotExist):
            BankTransaction.objects.get(label=edit['label'])

        # Finally test adding tag.
        form = self.app.get(url, user='superowner').form
        edit = {
            'label': 'test tags',
            'amount': '-154.12',
            'tag': str(tag1.pk),
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        banktransaction = BankTransaction.objects.get(label=edit['label'])
        self.assertEqual(
            str(banktransaction.tag.pk),
            edit['tag']
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_create_form(self):

        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('currency', form.fields)
        self.assertNotIn('scheduled', form.fields)

        edit = {
            'label': 'test create',
            'amount': '-187.41',
            'memo': "OMG, I didn't remember!",
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        banktransaction = BankTransaction.objects.get(label=edit['label'])
        self.assertEqual(banktransaction.amount, Decimal(edit['amount']))
        self.assertEqual(banktransaction.currency, self.bankaccount.currency)
        self.assertEqual(banktransaction.bankaccount.pk, self.bankaccount.pk)
        self.assertTrue(banktransaction.date)
        self.assertFalse(banktransaction.reconciled)
        self.assertEqual(banktransaction.payment_method, BankTransaction.PAYMENT_METHOD_CREDIT_CARD)
        self.assertEqual(banktransaction.memo, edit['memo'])
        self.assertFalse(banktransaction.scheduled)

        self.bankaccount.refresh_from_db()
        self.assertEqual(self.bankaccount.balance, Decimal('-187.41'))

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction %(label)s was created successfully.' % {
                'label': banktransaction.label
            },
            [message.message for message in storage],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_update_form(self):

        tag = BankTransactionTagFactory(owner=self.superowner)

        banktransaction = BankTransactionFactory(
            bankaccount=self.bankaccount,
            amount='-78.26',
            date='2015-07-10',
            reconciled=False,
            payment_method=BankTransaction.PAYMENT_METHOD_CREDIT_CARD,
            memo="",
            tag=BankTransactionTagFactory(),
        )

        url = reverse('banktransactions:update', kwargs={
            'pk': banktransaction.pk
        })

        form = self.app.get(url, user='superowner').form
        self.assertNotIn('currency', form.fields)
        self.assertNotIn('scheduled', form.fields)

        edit = {
            'label': 'test update',
            'amount': '15.69',
            'date': '2015-01-01',
            'reconciled': True,
            'payment_method': BankTransaction.PAYMENT_METHOD_CASH,
            'memo': "Ooops, typo errors!",
            'tag': str(tag.pk),
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        banktransaction.refresh_from_db()
        self.assertEqual(banktransaction.label, edit['label'])
        self.assertEqual(banktransaction.amount, Decimal(edit['amount']))
        self.assertEqual(banktransaction.currency, self.bankaccount.currency)
        self.assertEqual(banktransaction.bankaccount.pk, self.bankaccount.pk)
        self.assertEqual(
            str(banktransaction.date),
            edit['date'],
        )
        self.assertTrue(banktransaction.reconciled)
        self.assertEqual(banktransaction.payment_method, BankTransaction.PAYMENT_METHOD_CASH)
        self.assertEqual(banktransaction.memo, edit['memo'])
        self.assertFalse(banktransaction.scheduled)
        self.assertEqual(
            str(banktransaction.tag.pk),
            edit['tag'],
        )

        banktransaction.bankaccount.refresh_from_db()
        self.assertEqual(banktransaction.bankaccount.balance, Decimal('15.69'))

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction %(label)s was updated successfully.' % {
                'label': banktransaction.label
            },
            [message.message for message in storage],
        )

    def test_delete_form(self):

        banktransaction = BankTransactionFactory(bankaccount=self.bankaccount)

        url = reverse('banktransactions:delete', kwargs={
            'pk': banktransaction.pk
        })

        response = self.app.get(url, user='superowner')
        response = response.click(description=_('Cancel'))
        self.assertEqual(
            response.request.path,
            reverse('banktransactions:list', kwargs={
                'bankaccount_pk': self.bankaccount.pk,
            })
        )
        banktransaction.refresh_from_db()

        response = (
            self.app.get(url, user='superowner')
            .form.submit()
            .maybe_follow()
        )
        self.assertEqual(
            response.request.path,
            reverse('banktransactions:list', kwargs={
                'bankaccount_pk': self.bankaccount.pk
            })
        )
        with self.assertRaises(BankTransaction.DoesNotExist):
            banktransaction.refresh_from_db()

    def test_redirect_form(self):

        # Check on create form.
        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertFalse(form['redirect'].checked)
        edit = {
            'label': 'test redirect',
            'amount': '-50',
            'redirect': True,
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit()
        self.assertRedirects(response, url + '?self-redirect=1')
        response = response.maybe_follow()
        self.assertTrue(response.form['redirect'].checked)

        # Not on update form.
        banktransaction = BankTransactionFactory(bankaccount=self.bankaccount)
        url = reverse('banktransactions:update', kwargs={
            'pk': banktransaction.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('redirect', form.fields)


class ListFormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_fields(self):

        tag1 = BankTransactionTagFactory(owner=self.superowner)
        tag2 = BankTransactionTagFactory(owner=self.superowner)
        BankTransactionTagFactory()

        banktransactions = [
            BankTransactionFactory(bankaccount=self.bankaccount),
            BankTransactionFactory(bankaccount=self.bankaccount),
            BankTransactionFactory(bankaccount=self.bankaccount),
        ]

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='superowner').form

        self.assertListEqual(
            sorted([option[0] for option in form['tags'].options]),
            [str(tag1.pk), str(tag2.pk)]
        )

        for banktransaction in banktransactions:
            self.assertIn(
                'banktransaction_' + str(banktransaction.pk),
                form.fields
            )

        self.assertListEqual(
            ['delete', 'reconcile', 'unreconcile'],
            sorted([option[0] for option in form['operation'].options])
        )

        form = self.app.get(url, user='owner').form
        self.assertNotIn('operation', form.fields)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_clean(self):

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='superowner').form
        form['date_start'] = '2015-05-11'
        form['date_end'] = '2015-05-10'
        response = form.submit('filter').maybe_follow()
        self.assertFormError(
            response,
            'form',
            None,
            ['Date start could not be greater than date end.'],
        )

        form = self.app.get(url, user='superowner').form
        form['amount_min'] = 200
        form['amount_max'] = 100
        response = form.submit('filter').maybe_follow()
        self.assertFormError(
            response,
            'form',
            None,
            ['Minimum amount could not be greater than maximum amount.'],
        )

        form = self.app.get(url, user='superowner').form
        response = form.submit('action').maybe_follow()
        self.assertFormError(
            response,
            'form',
            None,
            ['To apply operations, you need to select some bank transactions.'],
        )
