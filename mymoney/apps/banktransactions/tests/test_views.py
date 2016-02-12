import datetime
import time
from decimal import Decimal

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import TestCase, modify_settings, override_settings
from django.utils.translation import ugettext as _

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactiontags.factories import \
    BankTransactionTagFactory
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionFactory
from ..models import BankTransaction
from ..views import BankTransactionListView


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
        cls.banktransaction = BankTransactionFactory(bankaccount=cls.bankaccount)

    def test_access_list(self):
        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_create(self):
        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Missing permission.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Having permission but not owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permission.
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank account.
        url = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': 20120918,
        })
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.logout()

    def test_access_update(self):
        url = reverse('banktransactions:update', kwargs={
            'pk': self.banktransaction.pk
        })

        # Anonymous
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non-owner with permissions.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        # Fake bank transaction.
        url = reverse('banktransactions:update', kwargs={
            'pk': 20140923
        })
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.client.logout()

    def test_access_delete(self):
        url = reverse('banktransactions:delete', kwargs={
            'pk': self.banktransaction.pk
        })

        # Anonymous
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non-owner with permissions.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

    def test_access_delete_multiple(self):

        url = reverse('banktransactions:delete_multiple', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous
        response = self.client.get(url)
        session = self.client.session
        session['banktransactionlistdelete'] = (self.banktransaction.pk,)
        session.save()
        self.assertEqual(403, response.status_code)

        # Non-owner with permissions.
        self.client.force_login(self.not_owner)
        session = self.client.session
        session['banktransactionlistdelete'] = (self.banktransaction.pk,)
        session.save()
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner without perm.
        self.client.force_login(self.owner)
        session = self.client.session
        session['banktransactionlistdelete'] = (self.banktransaction.pk,)
        session.save()
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions but without session value.
        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permission and an old bank transactions.
        self.client.force_login(self.superowner)
        session = self.client.session
        session['banktransactionlistdelete'] = (-15614,)
        session.save()
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.logout()

        # Owner with permissions and session value.
        self.client.force_login(self.superowner)
        session = self.client.session
        session['banktransactionlistdelete'] = (self.banktransaction.pk,)
        session.save()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

        self.client.force_login(self.superowner)
        session = self.client.session
        session['banktransactionlistdelete'] = (self.banktransaction.pk,)
        session.save()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.logout()

    def test_access_calendar_view(self):

        url = reverse('banktransactions:calendar', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_calendar_ajax_events(self):

        url = reverse('banktransactions:calendar_ajax_events', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        }) + '?from=0&to=0'

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_calendar_ajax_event(self):

        banktransaction = BankTransactionFactory(bankaccount=self.bankaccount)

        url = reverse('banktransactions:calendar_ajax_event', kwargs={
            'pk': banktransaction.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.force_login(self.not_owner)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.force_login(self.owner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.client.force_login(self.superowner)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


class ListTemplateTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(
            owners=[cls.owner, cls.superowner],
            balance_initial=Decimal('10.15'),
        )
        cls.banktransaction = BankTransactionFactory(bankaccount=cls.bankaccount)

    def test_link(self):

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        edit_url = reverse('banktransactions:update', kwargs={
            'pk': self.banktransaction.pk
        })
        delete_url = reverse('banktransactions:delete', kwargs={
            'pk': self.banktransaction.pk
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

    @override_settings(LANGUAGE_CODE='en-us')
    def test_no_previous_reconciled_total(self):

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        response = self.app.get(url, user='superowner')
        self.assertContains(response, '<td>+10.15</td>', html=True)


class ListViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.superowner),
            BankTransactionTagFactory(),
        ]
        cls.url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': cls.bankaccount.pk
        })

    @override_settings(LANGUAGE_CODE='en-us')
    def test_default_value(self):

        form = self.app.get(self.url, user='owner').form
        self.assertEqual(form['label'].value, '')
        self.assertEqual(form['date_start'].value, '')
        self.assertEqual(form['date_end'].value, '')
        self.assertEqual(form['amount_min'].value, '')
        self.assertEqual(form['amount_max'].value, '')
        self.assertEqual(form['status'].value, '')
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)

        fields = {
            'label': 'test',
            'date_start': '2015-05-11',
            'date_end': '2015-05-12',
            'amount_min': '-1500',
            'amount_max': '1500',
            'status': BankTransaction.STATUS_INACTIVE,
            'reconciled': '2',
            'tags': [
                str(self.banktransactiontags[0].pk),
                str(self.banktransactiontags[1].pk)
            ],
        }
        for name, value in fields.items():
            form[name] = value
        form = form.submit('filter').maybe_follow().form

        self.assertEqual(fields['label'], form['label'].value)
        self.assertEqual(
            fields['date_start'],
            form['date_start'].value,
        )
        self.assertEqual(
            fields['date_end'],
            form['date_end'].value,
        )
        self.assertEqual(fields['amount_min'], form['amount_min'].value)
        self.assertEqual(fields['amount_max'], form['amount_max'].value)
        self.assertEqual(fields['status'], form['status'].value)
        self.assertEqual(fields['reconciled'], form['reconciled'].value)
        self.assertListEqual(sorted(fields['tags']), sorted(form['tags'].value))

        # Test manual reset
        form['label'] = ''
        form['date_start'] = ''
        form['date_end'] = ''
        form['amount_min'] = ''
        form['amount_max'] = ''
        form['status'] = ''
        form['reconciled'] = '1'
        form['tags'].force_value(None)
        response = form.submit('filter').maybe_follow()
        form = response.form

        self.assertEqual(response.status_code, 200)
        self.assertEqual(form['label'].value, '')
        self.assertEqual(form['date_start'].value, '')
        self.assertEqual(form['date_end'].value, '')
        self.assertEqual(form['amount_min'].value, '')
        self.assertEqual(form['amount_max'].value, '')
        self.assertEqual(form['status'].value, '')
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)

    @override_settings(
        LANGUAGE_CODE='fr-fr',
        DATETIME_INPUT_FORMATS=('%d/%m/%Y',),
        DECIMAL_SEPARATOR=',',
    )
    def test_default_value_localize(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            date=datetime.date(2015, 5, 11),
            amount="15.59",
        )
        bt2 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            date=datetime.date(2015, 5, 12),
            amount="-25.59",
        )

        form = self.app.get(url, user='owner').form

        fields = {
            'date_start': '11/05/2015',
            'date_end': '11/05/2015',
        }
        for name, value in fields.items():
            form[name] = value
        response = form.submit('filter').maybe_follow()
        form = response.form

        self.assertEqual(
            fields['date_start'],
            form['date_start'].value,
        )
        self.assertEqual(
            fields['date_end'],
            form['date_end'].value,
        )
        self.assertListEqual(
            response.context[0].get('object_list', []),
            [bt1],
        )
        response = form.submit('reset').maybe_follow()
        form = response.form

        fields = {
            'amount_min': '10,26',
            'amount_max': '20,5',
        }
        for name, value in fields.items():
            form[name] = value
        response = form.submit('filter').maybe_follow()
        form = response.form

        self.assertEqual(fields['amount_min'], form['amount_min'].value)
        self.assertEqual(fields['amount_max'], form['amount_max'].value)
        self.assertListEqual(
            response.context[0].get('object_list', []),
            [bt1],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_reset(self):

        form = self.app.get(self.url, user='owner').form
        form = form.submit('reset').maybe_follow().form

        fields = {
            'label': 'test',
            'date_start': '2015-05-11',
            'date_end': '2015-05-11',
            'amount_min': '-1500',
            'amount_max': '1500',
            'status': BankTransaction.STATUS_INACTIVE,
            'reconciled': '2',
            'tags': [
                str(self.banktransactiontags[0].pk),
                str(self.banktransactiontags[1].pk),
            ],
        }
        for name, value in fields.items():
            form[name] = value
        form.submit('filter').maybe_follow()

        form.submit('reset').maybe_follow()
        form = self.app.get(self.url, user='owner').form
        self.assertFalse(form['label'].value)
        self.assertFalse(form['date_start'].value)
        self.assertFalse(form['date_end'].value)
        self.assertFalse(form['amount_min'].value)
        self.assertFalse(form['amount_max'].value)
        self.assertEqual(form['status'].value, '')
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_action_reconcile(self):

        bankaccount = BankAccountFactory(owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.59',
        )
        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-15.59',
        )

        form = self.app.get(url, user='superowner').form
        for bt in [bt1, bt2]:
            form['banktransaction_' + str(bt.pk)] = True
        form['operation'] = 'reconcile'
        response = form.submit('action').maybe_follow()

        for bt in [bt1, bt2]:
            bt.refresh_from_db()
            self.assertTrue(bt.reconciled)

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction have been reconciled.',
            [message.message for message in storage],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_action_unreconcile(self):

        bankaccount = BankAccountFactory(owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.59',
            reconciled=True,
        )
        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-15.59',
            reconciled=True,
        )

        form = self.app.get(url, user='superowner').form
        for bt in [bt1, bt2]:
            form['banktransaction_' + str(bt.pk)] = True
        form['operation'] = 'unreconcile'
        response = form.submit('action').maybe_follow()

        for bt in [bt1, bt2]:
            bt.refresh_from_db()
            self.assertFalse(bt.reconciled)

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Undo bank transaction reconciled.',
            [message.message for message in storage],
        )

    def test_action_delete(self):

        bankaccount = BankAccountFactory(owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.59',
        )
        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-15.59',
        )
        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='75',
        )
        balance = bankaccount.balance

        form = self.app.get(url, user='superowner').form
        for bt in [bt1, bt2, bt3]:
            form['banktransaction_' + str(bt.pk)] = True
        form['operation'] = 'delete'
        response = form.submit('action').maybe_follow()

        # Test cancel link
        response = response.click(description=_("Cancel"))
        self.assertEqual(
            response.request.path,
            reverse('banktransactions:list', kwargs={
                'bankaccount_pk': bankaccount.pk,
            })
        )

        # Is delete somewhere else.
        bt3.delete()
        balance -= Decimal(75)

        # Direct access on multiple delete page. Session is not up-to-date.
        form = self.app.get(
            reverse('banktransactions:delete_multiple', kwargs={
                'bankaccount_pk': bankaccount.pk
            })
        ).form
        response = form.submit().maybe_follow()

        self.assertFalse(
            list(BankTransaction.objects.filter(pk__in=[bt1.pk, bt2.pk]))
        )
        bankaccount.refresh_from_db()
        self.assertEqual(
            bankaccount.balance,
            balance - Decimal('5.59') - Decimal('-15.59')
        )

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transactions deleted successfully.',
            [message.message for message in storage],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_filter(self):

        bankaccount = BankAccountFactory(owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        banktransactions = [
            BankTransactionFactory(
                bankaccount=bankaccount,
                label="credit",
                amount="15.59",
                date=datetime.date(2015, 5, 11),
                tag=self.banktransactiontags[0],
                reconciled=True,
            ),
            BankTransactionFactory(
                bankaccount=bankaccount,
                amount="-25.59",
                date=datetime.date(2015, 5, 12),
            ),
        ]

        form = self.app.get(url, user='superowner').form
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [
                banktransactions[0].pk,
                banktransactions[1].pk,
            ],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['label'] = 'rEDi'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['date_start'] = '2015-05-11'
        form['date_end'] = '2015-05-11'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list', {})
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['date_start'] = '2015-05-12'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[1].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['date_end'] = '2015-05-11'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['amount_min'] = '0'
        form['amount_max'] = '20'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['amount_min'] = '0'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['amount_max'] = '0'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[1].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['status'] = BankTransaction.STATUS_ACTIVE
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [
                banktransactions[0].pk,
                banktransactions[1].pk,
            ],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['status'] = BankTransaction.STATUS_INACTIVE
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(list(object_list), []),
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['reconciled'] = '2'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['reconciled'] = '3'
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[1].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['tags'] = [str(self.banktransactiontags[0].pk)]
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['tags'] = [
            str(self.banktransactiontags[0].pk),
            str(self.banktransactiontags[2].pk),
        ]
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

        form = self.app.get(url, user='superowner').form
        form['label'] = 'credit'
        form['amount_min'] = '15.55'
        form['date_end'] = '2015-05-11'
        form['reconciled'] = '2'
        form['status'] = BankTransaction.STATUS_ACTIVE
        form['tags'] = [str(self.banktransactiontags[0].pk)]
        response = form.submit('filter').maybe_follow()
        object_list = response.context[0].get('object_list')
        self.assertListEqual(
            sorted([obj.pk for obj in object_list]),
            [banktransactions[0].pk],
        )
        form.submit('reset').maybe_follow()

    def test_paginator(self):

        # Monkey patch just to reduce it.
        BankTransactionListView.paginate_by = 5

        limit = BankTransactionListView.paginate_by
        count = BankTransaction.objects\
            .filter(bankaccount=self.bankaccount)\
            .count()

        for i in range(0, limit - count + 1):
            BankTransactionFactory(bankaccount=self.bankaccount)

        response = self.app.get(self.url, user='superowner')
        self.assertEqual(len(response.context[0].get('object_list')), limit)

        response = self.app.get(self.url + '?page=2', user='superowner')
        self.assertEqual(len(response.context[0].get('object_list')), 1)

        response = self.app.get(self.url + '?page=465465456', user='superowner')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[0].get('object_list')), limit)

        response = self.app.get(self.url + '?page=foo', user='superowner')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[0].get('object_list')), limit)

    def test_reconciled_balance(self):

        bankaccount = BankAccountFactory(balance=0, owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-15.59',
            date=datetime.date(2015, 6, 3),
        )
        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-4.41',
            reconciled=True,
            date=datetime.date(2015, 6, 3),
        )
        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.00',
            reconciled=True,
            date=datetime.date(2015, 6, 3),
        )
        bt4 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.59',
            date=datetime.date(2015, 6, 4),
        )
        bt5 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount='6.59',
            reconciled=True,
            date=datetime.date(2015, 6, 4),
        )

        response = self.app.get(url, user='superowner')
        object_list = list(reversed(response.context[0].get('object_list')))
        self.assertListEqual(
            [obj.pk for obj in object_list],
            [bt1.pk, bt2.pk, bt3.pk, bt4.pk, bt5.pk],
        )

        self.assertListEqual(
            [obj.reconciled_balance for obj in object_list],
            [
                # None, which should be balance initial instead. But this is
                # done in the template to prevent useless queryset loop just
                # for this special use case.
                None,
                Decimal('-4.41'),  # First reconciled bank transaction.
                Decimal('0.59'),  # -4.41 + 5
                Decimal('0.59'),  # Not reconciled, so previous value: 0.59
                Decimal('7.18'),  # 0.59 + 6.59
            ],
        )

        bankaccount.balance_initial = Decimal('150')
        bankaccount.save()

        response = self.app.get(url, user='superowner')
        object_list = list(reversed(response.context[0].get('object_list')))
        self.assertListEqual(
            [obj.reconciled_balance for obj in object_list],
            [
                None,
                Decimal('150') + Decimal('-4.41'),
                Decimal('150') + Decimal('0.59'),
                Decimal('150') + Decimal('0.59'),
                Decimal('150') + Decimal('7.18'),
            ],
        )

    def test_total_balance(self):

        bankaccount = BankAccountFactory(balance=0, owners=[self.superowner])

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-15.59',
            date=datetime.date(2015, 6, 3),
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount='-4.41',
            date=datetime.date(2015, 6, 3),
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.00',
            date=datetime.date(2015, 6, 3),
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount='5.59',
            date=datetime.date(2015, 6, 4),
        )
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount='6.59',
            date=datetime.date(2015, 6, 4),
        )
        bankaccount.refresh_from_db()
        self.assertEqual(bankaccount.balance, Decimal('-2.82'))

        response = self.app.get(url, user='superowner')
        object_list = list(reversed(response.context[0].get('object_list')))
        self.assertListEqual(
            [obj.total_balance for obj in object_list],
            [
                Decimal('-15.59'),
                Decimal('-20'),
                Decimal('-15'),
                Decimal('-9.41'),
                Decimal('-2.82'),
            ],
        )

        bankaccount.balance_initial = Decimal('150')
        bankaccount.save()

        response = self.app.get(url, user='superowner')
        object_list = list(reversed(response.context[0].get('object_list')))
        self.assertListEqual(
            [obj.total_balance for obj in object_list],
            [
                Decimal('150') + Decimal('-15.59'),
                Decimal('150') + Decimal('-20'),
                Decimal('150') + Decimal('-15'),
                Decimal('150') + Decimal('-9.41'),
                Decimal('150') + Decimal('-2.82'),
            ],
        )


class CalendarViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])

    def test_context_data(self):

        url = reverse('banktransactions:calendar', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })

        with self.settings(MYMONEY={"USE_L10N_DIST": True}):
            response = self.app.get(url, user='owner')
            self.assertNotIn('bootstrap_calendar_langcode', response.context[0])

        with self.settings(MYMONEY={"USE_L10N_DIST": False, "BOOTSTRAP_CALENDAR_LANGCODE": ""}):
            response = self.app.get(url, user='owner')
            self.assertNotIn('bootstrap_calendar_langcode', response.context[0])

        with self.settings(MYMONEY={"USE_L10N_DIST": False, "BOOTSTRAP_CALENDAR_LANGCODE": "fr-FR"}):
            response = self.app.get(url, user='owner')
            self.assertIn('bootstrap_calendar_langcode', response.context[0])
            self.assertTrue(
                response.context[0]['bootstrap_calendar_langcode'].endswith('fr-FR.js')
            )

    def test_view(self):

        url = reverse('banktransactions:calendar', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })

        response = self.app.get(url, user='owner')
        self.assertEqual(
            response.context[0]['bankaccount'],
            self.bankaccount,
        )
        self.assertEqual(
            response.context[0]['calendar_ajax_url'],
            reverse(
                'banktransactions:calendar_ajax_events',
                kwargs={
                    'bankaccount_pk': self.bankaccount.pk,
                },
            )
        )


class CalendarEventsAjaxTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_bad_request(self):

        base_url = reverse('banktransactions:calendar_ajax_events', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })

        timestamp_ms = str(int(time.mktime(datetime.date(2015, 8, 23).timetuple())) * 1000)

        url = base_url + '?from=foo&to=' + timestamp_ms
        response = self.app.get(url, user='owner', status=400)
        self.assertEqual(response.status_code, 400)

        url = base_url + '?from=' + timestamp_ms + '&to=1000000000000000'
        response = self.app.get(url, user='owner', status=400)
        self.assertEqual(response.status_code, 400)

        url = base_url + '?from=-100000000000000&to=' + timestamp_ms
        response = self.app.get(url, user='owner', status=400)
        self.assertEqual(response.status_code, 400)

    def test_ajax_response(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        base_url = reverse('banktransactions:calendar_ajax_events', kwargs={
            'bankaccount_pk': bankaccount.pk,
        })

        start = str(int(time.mktime(datetime.date(2015, 7, 27).timetuple())) * 1000)
        end = str(int(time.mktime(datetime.date(2015, 8, 31).timetuple())) * 1000)

        url = base_url + '?from={start}&to={end}'.format(start=start, end=end)

        response = self.app.get(url, user='owner')
        self.assertIn("success", response.json)
        self.assertEqual(response.json["success"], 1)
        self.assertFalse(response.json["result"])

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('10'),
            date=datetime.date(2015, 7, 27),
            reconciled=True,
        )

        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('10'),
            date=datetime.date(2015, 7, 31),
            reconciled=True,
        )

        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-30'),
            date=datetime.date(2015, 8, 31),
        )

        bt4 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            date=datetime.date(2015, 9, 10),
        )

        response = self.app.get(url, user='owner')
        result = response.json['result']
        self.assertListEqual(
            [event['id'] for event in result],
            [bt1.pk, bt2.pk, bt3.pk],
        )
        self.assertListEqual(
            [Decimal(event['extra_data']['total_balance']) for event in result],
            [
                bt1.amount,
                bt1.amount + bt2.amount,
                bt1.amount + bt2.amount + bt3.amount,
            ],
        )
        self.assertListEqual(
            [Decimal(event['extra_data']['reconciled_balance']) for event in result],
            [
                bt1.amount,
                bt1.amount + bt2.amount,
                bt1.amount + bt2.amount,
            ],
        )


class CalendarEventAjaxTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_not_found(self):

        url = reverse('banktransactions:calendar_ajax_event', kwargs={'pk': 0})
        response = self.app.get(url, user='owner', status=404)
        self.assertEqual(response.status_code, 404)

    def test_context_data(self):

        bankaccount = BankAccountFactory(owners=[self.owner, self.superowner])
        banktransaction = BankTransactionFactory(bankaccount=bankaccount)
        url = reverse('banktransactions:calendar_ajax_event', kwargs={
            'pk': banktransaction.pk,
        })

        response = self.app.get(url, user='owner')
        self.assertEqual(
            response.context['banktransaction'].pk,
            banktransaction.pk,
        )
        self.assertNotIn('edit_url', response.context)
        self.assertNotIn('delete_url', response.context)

        response = self.app.get(url, user='superowner')
        self.assertEqual(
            response.context['banktransaction'].pk,
            banktransaction.pk,
        )
        self.assertEqual(
            response.context['url_edit'],
            reverse('banktransactions:update', kwargs={'pk': banktransaction.pk})
        )
        self.assertEqual(
            response.context['url_delete'],
            reverse('banktransactions:delete', kwargs={'pk': banktransaction.pk})
        )
