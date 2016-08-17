from decimal import Decimal

from django.contrib import messages
from django.urls import reverse
from django.test import override_settings
from django.utils.translation import ugettext as _

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactiontags.factories import \
    BankTransactionTagFactory
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionSchedulerFactory
from ..models import BankTransactionScheduler


class FormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.superowner])

    @override_settings(LANGUAGE_CODE='en-us')
    def test_create_form(self):

        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('bankaccount', form.fields)
        self.assertNotIn('currency', form.fields)
        self.assertNotIn('reconciled', form.fields)
        self.assertNotIn('scheduled', form.fields)
        self.assertNotIn('last_action', form.fields)
        self.assertNotIn('state', form.fields)

        edit = {
            'label': 'rent scheduled',
            'amount': '-800',
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        banktransactionscheduler = BankTransactionScheduler.objects.get(
            label=edit['label']
        )
        self.assertEqual(banktransactionscheduler.amount, Decimal('-800'))
        self.assertEqual(
            banktransactionscheduler.status,
            BankTransactionScheduler.STATUS_ACTIVE
        )
        self.assertEqual(
            banktransactionscheduler.type,
            BankTransactionScheduler.TYPE_MONTHLY
        )
        self.assertIsNone(banktransactionscheduler.recurrence)
        self.assertIsNone(banktransactionscheduler.last_action)
        self.assertEqual(
            banktransactionscheduler.state,
            BankTransactionScheduler.STATE_WAITING
        )

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction scheduler %(label)s was created successfully.' % {
                'label': banktransactionscheduler.label
            },
            [message.message for message in storage],
        )

    def test_create_form_start_now(self):

        url = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        count = BankTransaction.objects.filter(bankaccount=self.bankaccount).count()

        form = self.app.get(url, user='superowner').form
        self.assertIn('start_now', form.fields)

        edit = {
            'label': 'rent scheduled',
            'amount': '-800',
            'start_now': True,
        }
        for name, value in edit.items():
            form[name] = value
        form.submit().maybe_follow()

        self.assertEqual(
            BankTransaction.objects.filter(bankaccount=self.bankaccount).count(),
            count + 1,
        )

        bt_clone = (BankTransaction.objects
                    .filter(bankaccount=self.bankaccount.pk)
                    .order_by()
                    .last())
        self.assertEqual(bt_clone.label, edit['label'])
        self.assertEqual(bt_clone.amount, Decimal(edit['amount']))

    @override_settings(LANGUAGE_CODE='en-us')
    def test_update_form(self):

        tag1 = BankTransactionTagFactory(owner=self.superowner)
        tag2 = BankTransactionTagFactory(owner=self.superowner)

        banktransactionscheduler = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
            tag=tag1,
            type=BankTransactionScheduler.TYPE_MONTHLY,
            recurrence=None,
            status=BankTransactionScheduler.STATUS_ACTIVE,
        )

        url = reverse('banktransactionschedulers:update', kwargs={
            'pk': banktransactionscheduler.pk
        })

        form = self.app.get(url, user='superowner').form
        self.assertNotIn('bankaccount', form.fields)
        self.assertNotIn('currency', form.fields)
        self.assertNotIn('reconciled', form.fields)
        self.assertNotIn('scheduled', form.fields)
        self.assertNotIn('last_action', form.fields)
        self.assertNotIn('state', form.fields)

        edit = {
            'amount': '-789.45',
            'tag': str(tag2.pk),
            'type': BankTransactionScheduler.TYPE_WEEKLY,
            'recurrence': 10,
            'status': BankTransactionScheduler.STATUS_INACTIVE,
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit().maybe_follow()

        banktransactionscheduler.refresh_from_db()

        self.assertEqual(
            banktransactionscheduler.amount,
            Decimal(edit['amount'])
        )
        self.assertEqual(banktransactionscheduler.tag.pk, tag2.pk)
        self.assertEqual(
            banktransactionscheduler.type,
            BankTransactionScheduler.TYPE_WEEKLY
        )
        self.assertEqual(
            banktransactionscheduler.recurrence,
            edit['recurrence']
        )
        self.assertEqual(
            banktransactionscheduler.status,
            edit['status']
        )

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction scheduler %(label)s was updated successfully.' % {
                'label': banktransactionscheduler.label
            },
            [message.message for message in storage],
        )

    def test_delete_form(self):

        banktransactionscheduler = BankTransactionSchedulerFactory(
            bankaccount=self.bankaccount,
        )

        url = reverse('banktransactionschedulers:delete', kwargs={
            'pk': banktransactionscheduler.pk
        })
        bankaccount_pk = banktransactionscheduler.bankaccount.pk

        response = self.app.get(url, user='superowner')
        response = response.click(description=_('Cancel'))
        self.assertEqual(
            response.request.path,
            reverse('banktransactionschedulers:list', kwargs={
                'bankaccount_pk': bankaccount_pk
            })
        )
        banktransactionscheduler.refresh_from_db()

        response = (
            self.app.get(url, user='superowner')
            .form.submit()
            .maybe_follow()
        )
        self.assertEqual(
            response.request.path,
            reverse('banktransactionschedulers:list', kwargs={
                'bankaccount_pk': bankaccount_pk
            })
        )
        with self.assertRaises(BankTransactionScheduler.DoesNotExist):
            banktransactionscheduler.refresh_from_db()

    def test_redirect_form(self):

        # Check on create form.
        url = reverse('banktransactionschedulers:create', kwargs={
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
        form = response.form
        self.assertTrue(form['redirect'].checked)

        edit = {
            'label': 'test redirect',
            'amount': '-50',
            'redirect': False,
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit()
        self.assertRedirects(response, reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        }))

        # Not on update form.
        scheduler = BankTransactionSchedulerFactory(bankaccount=self.bankaccount)
        url = reverse('banktransactionschedulers:update', kwargs={
            'pk': scheduler.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('redirect', form.fields)
