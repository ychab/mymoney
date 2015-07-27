import datetime
import json
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactiontags.factories import BankTransactionTagFactory
from mymoney.core.factories import UserFactory
from mymoney.core.utils.dates import GRANULARITY_MONTH, GRANULARITY_WEEK

from ..forms import RatioForm, TrendtimeForm


class AccessTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.not_owner),
        ]

    def test_access_ratio(self):
        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_ratio_summary(self):

        url = reverse('banktransactionanalytics:ratiosummary', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
            'tag_id': self.banktransactiontags[0].pk,
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner without session filter.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner with session filter.
        self.client.login(username=self.not_owner, password='test')
        session = self.client.session
        session['banktransactionanalyticratioform'] = {
            'filters': {
                'date_start': '2015-06-22',
                'date_end': '2015-06-22',
                'type': RatioForm.DEBIT,
            },
        }
        session.save()
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner with session filter but wrong tag ID.
        self.client.login(username=self.owner, password='test')
        session = self.client.session
        session['banktransactionanalyticratioform'] = {
            'filters': {
                'date_start': '2015-06-22',
                'date_end': '2015-06-22',
                'type': RatioForm.DEBIT,
            },
        }
        session.save()
        response = self.client.get(reverse(
            'banktransactionanalytics:ratiosummary',
            kwargs={
                'bankaccount_pk': self.bankaccount.pk,
                'tag_id': self.banktransactiontags[1].pk,
            },
        ))
        self.assertEqual(403, response.status_code)
        # Owner with filter and no tag id.
        response = self.client.get(reverse(
            'banktransactionanalytics:ratiosummary',
            kwargs={
                'bankaccount_pk': self.bankaccount.pk,
                'tag_id': 0,
            },
        ))
        self.assertEqual(200, response.status_code)
        # Finally owner with session filter and good tag ID.
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_trendtime(self):
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_access_trendtime_summary(self):
        url = reverse('banktransactionanalytics:trendtimesummary', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
            'year': '2015',
            'month': '6',
            'day': '9',
        })

        # Anonymous denied
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Non owner.
        self.client.login(username=self.not_owner, password='test')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        # Owner.
        self.client.login(username=self.owner, password='test')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


class RatioViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):

        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
        ]

        cls.url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': cls.bankaccount.pk
        })

    def test_default_value(self):

        form = self.app.get(self.url, user='owner').form

        self.assertEqual(form['type'].value, RatioForm.DEBIT)
        self.assertEqual(form['chart'].value, RatioForm.CHART_DOUGHNUT)
        self.assertEqual(form['date_start'].value, '')
        self.assertEqual(form['date_end'].value, '')
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)
        self.assertEqual(form['sum_min'].value, '')
        self.assertEqual(form['sum_max'].value, '')

        fields = {
            'type': RatioForm.CREDIT,
            'chart': RatioForm.CHART_POLAR,
            'date_start': '2015-05-11',
            'date_end': '2015-05-11',
            'reconciled': '2',
            'tags': [
                str(self.banktransactiontags[0].pk),
                str(self.banktransactiontags[1].pk),
            ],
            'sum_min': '-1500',
            'sum_max': '1500',
        }
        for name, value in fields.items():
            form[name] = value
        form = form.submit('filter').maybe_follow().form

        self.assertEqual(fields['type'], form['type'].value)
        self.assertEqual(fields['chart'], form['chart'].value)
        self.assertEqual(
            str(datetime.date(2015, 5, 11)),
            form['date_start'].value,
        )
        self.assertEqual(
            str(datetime.date(2015, 5, 11)),
            form['date_end'].value,
        )
        self.assertEqual(fields['reconciled'], form['reconciled'].value)
        self.assertListEqual(sorted(fields['tags']), sorted(form['tags'].value))
        self.assertEqual(fields['sum_min'], form['sum_min'].value)
        self.assertEqual(fields['sum_max'], form['sum_max'].value)

        # Test manual reset
        form['type'] = RatioForm.DEBIT
        form['chart'] = RatioForm.CHART_DOUGHNUT
        form['date_start'] = ''
        form['date_end'] = ''
        form['reconciled'] = '1'
        form['tags'].force_value(None)
        form['sum_min'] = ''
        form['sum_max'] = ''
        response = form.submit('filter').maybe_follow()
        form = response.form

        self.assertEqual(response.status_code, 200)
        self.assertEqual(form['type'].value, RatioForm.DEBIT)
        self.assertEqual(form['chart'].value, RatioForm.CHART_DOUGHNUT)
        self.assertEqual(form['date_start'].value, '')
        self.assertEqual(form['date_end'].value, '')
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)
        self.assertEqual(form['sum_min'].value, '')
        self.assertEqual(form['sum_max'].value, '')

    @override_settings(
        LANGUAGE_CODE='fr-fr',
        DATETIME_INPUT_FORMATS=('%d/%m/%Y',),
        DECIMAL_SEPARATOR = ',',
    )
    def test_default_value_localize(self):

        form = self.app.get(self.url, user='owner').form

        fields = {
            'date_start': '12/05/2015',
            'date_end': '12/05/2015',
            'sum_min': '-300,79',
            'sum_max': '-200,15',
        }
        for name, value in fields.items():
            form[name] = value
        response = form.submit('filter').maybe_follow()
        form = response.form
        self.assertEqual(form['date_start'].value, fields['date_start'])
        self.assertEqual(form['date_end'].value, fields['date_end'])
        self.assertEqual(
            self.app.session['banktransactionanalyticratioform']['filters']['date_start'],
            str(datetime.datetime.strptime(fields['date_start'], '%d/%m/%Y').date())
        )
        self.assertEqual(
            self.app.session['banktransactionanalyticratioform']['filters']['date_end'],
            str(datetime.datetime.strptime(fields['date_end'], '%d/%m/%Y').date())
        )
        self.assertEqual(fields['sum_min'], form['sum_min'].value)
        self.assertEqual(fields['sum_max'], form['sum_max'].value)
        self.assertEqual(
            self.app.session['banktransactionanalyticratioform']['filters']['sum_min'],
            fields['sum_min'].replace(',', '.'),
        )
        self.assertEqual(
            self.app.session['banktransactionanalyticratioform']['filters']['sum_max'],
            fields['sum_max'].replace(',', '.'),
        )

    def test_reset(self):

        form = self.app.get(self.url, user='owner').form
        form = form.submit('reset').maybe_follow().form

        fields = {
            'type': RatioForm.CREDIT,
            'chart': RatioForm.CHART_POLAR,
            'date_start': '2015-05-11',
            'date_end': '2015-05-11',
            'reconciled': '2',
            'tags': [
                str(self.banktransactiontags[0].pk),
                str(self.banktransactiontags[1].pk),
            ],
            'sum_min': '-1500',
            'sum_max': '1500',
        }
        for name, value in fields.items():
            form[name] = value
        form.submit('filter').maybe_follow()
        form.submit('reset').maybe_follow()

        form = self.app.get(self.url, user='owner').form
        self.assertEqual(form['type'].value, RatioForm.DEBIT)
        self.assertEqual(form['chart'].value, RatioForm.CHART_DOUGHNUT)
        self.assertFalse(form['date_start'].value)
        self.assertFalse(form['date_end'].value)
        self.assertEqual(form['reconciled'].value, '1')
        self.assertIsNone(form['tags'].value)
        self.assertFalse(form['sum_min'].value)
        self.assertFalse(form['sum_max'].value)

    def test_success_url(self):

        form = self.app.get(self.url, user='owner').form
        form['date_start'] = '2015-06-18'
        form['date_end'] = '2015-06-19'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(self.url, response.request.path)

        response = response.form.submit('reset').maybe_follow()
        self.assertEqual(self.url, response.request.path)


class RatioQuerysetTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
        ]

    def test_queryset(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        # Test without session filter.
        response = self.app.get(url, user='owner')
        self.assertNotIn('total', response.context)
        self.assertNotIn('sub_total', response.context)
        self.assertNotIn('rows', response.context)
        self.assertNotIn('chart_data', response.context)

        # Test without bank transactions.
        form = self.app.get(url, user='owner').form
        form['date_start'] = '2012-06-10'
        form['date_end'] = '2018-06-20'
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('total', response.context)
        self.assertNotIn('sub_total', response.context)
        self.assertNotIn('rows', response.context)
        self.assertNotIn('chart_data', response.context)

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-06-13',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('165.23'),
            date='2015-06-13',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-06-14',
            tag=self.banktransactiontags[0],
        )

        bt4 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-134.00'),
            date='2015-06-15',
            tag=self.banktransactiontags[2],
        )

        # No tags
        bt5 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-45.88'),
            date='2015-06-15',
            reconciled=True,
        )

        # Inactive
        bt6 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_INACTIVE,
            tag=self.banktransactiontags[0],
        )

        # Another bank account
        bt7 = BankTransactionFactory(  # noqa
            bankaccount=BankAccountFactory(),
            amount=Decimal('-88.54'),
            date='2015-06-14',
            tag=self.banktransactiontags[0],
        )

        bt8 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('865.23'),
            date='2015-06-14',
        )

        # Ignored
        bt9 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
            tag=self.banktransactiontags[0],
        )

        # Default filter.
        form = form.submit('reset').maybe_follow().form
        form['date_start'] = '2015-06-10'
        form['date_end'] = '2015-06-20'
        response = form.submit('filter').maybe_follow()

        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount + bt3.amount,  # Decimal("-669.52")
                    "percentage": Decimal("78.82"),
                },
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("15.78"),
                },
                {
                    "tag_id": None,
                    "sum": bt5.amount,  # Decimal("-45.88")
                    "percentage": Decimal("5.40"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [78.82, 15.78, 5.4],
        )

        # Type filter.
        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.CREDIT
        form['date_start'] = '2015-06-10'
        form['date_end'] = '2015-06-20'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt2.amount + bt8.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt2.amount + bt8.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": None,
                    "sum": bt8.amount,  # Decimal("865.23")
                    "percentage": Decimal("83.97"),
                },
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt2.amount,  # Decimal("165.23")
                    "percentage": Decimal("16.03"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [83.97, 16.03],
        )

        # Date filter.
        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2016-06-10'
        form['date_end'] = '2016-06-20'
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('total', response.context)
        self.assertNotIn('sub_total', response.context)
        self.assertNotIn('rows', response.context)

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-13'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount,  # Decimal("-15.40")
                    "percentage": Decimal("100.00"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [100.0],
        )

        # Reconciled filter
        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['reconciled'] = '2'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount + bt5.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": None,
                    "sum": bt5.amount,  # Decimal("-45.88")
                    "percentage": Decimal("74.87"),
                },
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount,  # Decimal("-15.40")
                    "percentage": Decimal("25.13"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [74.87, 25.13],
        )

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['reconciled'] = '3'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt3.amount + bt4.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt3.amount + bt4.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt3.amount,  # Decimal("-654.12")
                    "percentage": Decimal("83.00"),
                },
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("17.00"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [83.0, 17.0],
        )

        # Tags filter.
        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['tags'] = [self.banktransactiontags[0].pk]
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount + bt3.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount + bt3.amount,  # Decimal("-669.52")
                    "percentage": Decimal("78.82"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [78.82],
        )

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['tags'] = [
            self.banktransactiontags[0].pk,
            self.banktransactiontags[2].pk,
        ]
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount + bt3.amount + bt4.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount + bt3.amount,  # Decimal("-669.52")
                    "percentage": Decimal("78.82"),
                },
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("15.78"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [78.82, 15.78],
        )

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['tags'] = [self.banktransactiontags[1].pk]
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(response.context['sub_total'], 0)
        self.assertFalse(response.context['rows'])
        self.assertNotIn('chart_data', response.context)

        # Sum filter
        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['sum_min'] = '-200'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt4.amount + bt5.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("15.78"),
                },
                {
                    "tag_id": None,
                    "sum": bt5.amount,  # Decimal("-45.88")
                    "percentage": Decimal("5.40"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [15.78, 5.40],
        )

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['sum_max'] = '-100'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt1.amount + bt3.amount + bt4.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[0].pk,
                    "sum": bt1.amount + bt3.amount,  # Decimal("-669.52")
                    "percentage": Decimal("78.82"),
                },
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("15.78"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [78.82, 15.78],
        )

        form = form.submit('reset').maybe_follow().form
        form['type'] = RatioForm.DEBIT
        form['date_start'] = '2015-06-13'
        form['date_end'] = '2015-06-18'
        form['sum_min'] = '-200'
        form['sum_max'] = '-100'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['total'],
            bt1.amount + bt3.amount + bt4.amount + bt5.amount,
        )
        self.assertEqual(
            response.context['sub_total'],
            bt4.amount,
        )
        self.assertListEqual(
            [{
                'tag_id': row['tag_id'],
                'sum': row['sum'],
                'percentage': row['percentage']
            } for row in response.context['rows']],
            [
                {
                    "tag_id": self.banktransactiontags[2].pk,
                    "sum": bt4.amount,  # Decimal("-134.00")
                    "percentage": Decimal("15.78"),
                },
            ],
        )
        self.assertListEqual(
            [row['value'] for row in json.loads(response.context['chart_data'])['data']],
            [15.78],
        )


class RatioListViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):

        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
        ]

        BankTransactionFactory(
            bankaccount=cls.bankaccount,
            date='2015-07-05',
            tag=cls.banktransactiontags[0],
        )
        BankTransactionFactory(
            bankaccount=cls.bankaccount,
            date='2015-07-05',
            tag=cls.banktransactiontags[1],
        )
        BankTransactionFactory(
            bankaccount=cls.bankaccount,
            date='2015-07-05',
        )

        cls.url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': cls.bankaccount.pk
        })

    @override_settings(LANGUAGE_CODE='en-us')
    def test_colors(self):

        form = self.app.get(self.url, user='owner').form
        form['date_start'] = '2010-01-01'
        form['date_end'] = '2020-12-31'
        form.submit('filter').maybe_follow()
        colors = self.app.session['banktransactionanalyticratioform']['colors']

        response = self.app.get(self.url, user='owner')
        self.assertDictEqual(
            colors,
            self.app.session['banktransactionanalyticratioform']['colors'],
        )

        response = response.form.submit('filter').maybe_follow()
        self.assertDictEqual(
            colors,
            self.app.session['banktransactionanalyticratioform']['colors'],
        )

        response = response.form.submit('reset').maybe_follow()
        self.assertNotIn(
            'banktransactionanalyticratioform',
            self.app.session,
        )

    def test_reset(self):

        # Required fields should be skipped for e.g, like other errors.
        form = self.app.get(self.url, user='owner').form
        form['sum_min'] = '15'
        form['sum_max'] = '10'
        response = form.submit('reset').maybe_follow()
        self.assertFalse(response.context['form'].errors)


class RatioSummaryViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.not_owner = UserFactory(username='not_owner', user_permissions='staff')
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.not_owner),
        ]

    @override_settings(LANGUAGE_CODE='en-us')
    def test_queryset(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url_form = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': bankaccount.pk
        })
        url_summary = reverse('banktransactionanalytics:ratiosummary', kwargs={
            'bankaccount_pk': bankaccount.pk,
            'tag_id': self.banktransactiontags[0].pk,
        })

        # Test without bank transactions and init filters.
        form = self.app.get(url_form, user='owner').form
        form['date_start'] = '2015-06-01'
        form['date_end'] = '2015-06-30'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertIn('banktransactions', response.context)
        self.assertFalse(response.context['banktransactions'])

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-06-13',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        bt2 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('165.23'),
            date='2015-06-20',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        # Not reconciled.
        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-06-05',
            tag=self.banktransactiontags[0],
        )

        # Too late
        bt4 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-134.00'),
            date='2015-12-20',
        )

        # No tags
        bt5 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-134.00'),
            date='2015-06-20',
        )

        # Other bank account
        bt6 = BankTransactionFactory(  # noqa
            bankaccount=BankAccountFactory(),
            amount=Decimal('-45.88'),
            date='2015-06-15',
            reconciled=True,
        )

        # Inactive
        bt7 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_INACTIVE,
        )

        # Other tag.
        bt8 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            tag=self.banktransactiontags[3],
        )

        # Ignored
        bt9 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
        )

        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt3), repr(bt1)],
        )

        response = self.app.get(reverse(
            'banktransactionanalytics:ratiosummary',
            kwargs={
                'bankaccount_pk': bankaccount.pk,
                'tag_id': 0,
            },
        ), user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt5)],
        )

        response = form.submit('reset').maybe_follow()
        form = response.form
        form['date_start'] = '2012-05-10'
        form['date_end'] = '2018-07-20'
        form['reconciled'] = '2'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt1)],
        )

        response = form.submit('reset').maybe_follow()
        form = response.form
        form['date_start'] = '2012-05-10'
        form['date_end'] = '2018-07-20'
        form['reconciled'] = '3'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt3)],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_ajax(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url_form = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': bankaccount.pk
        })
        url_summary = reverse('banktransactionanalytics:ratiosummary', kwargs={
            'bankaccount_pk': bankaccount.pk,
            'tag_id': self.banktransactiontags[0].pk,
        })

        form = self.app.get(url_form, user='owner').form
        form['date_start'] = '2015-06-01'
        form['date_end'] = '2015-06-30'
        form.submit('filter').maybe_follow()

        response = self.app.get(url_summary, user='owner', xhr=False)
        self.assertContains(
            response,
            "{bankaccount}'s ratio statistics summary".format(bankaccount=bankaccount),
        )

        response = self.app.get(url_summary, user='owner', xhr=True)
        self.assertNotContains(
            response,
            "{bankaccount}'s ratio statistics summary".format(bankaccount=bankaccount),
        )


class RatioTemplateTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_no_result(self):

        bankaccount = BankAccountFactory(owners=[self.owner])
        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        form = self.app.get(url, user='owner').form
        form['date_start'] = '2015-01-01'
        form['date_end'] = '2015-01-01'
        response = form.submit('filter').maybe_follow()
        self.assertContains(response, 'There is no result to your search.')


class TrendtimeViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])
        cls.url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': cls.bankaccount.pk
        })

    @override_settings(
        LANGUAGE_CODE='en-us',
        DATETIME_INPUT_FORMATS=('%m/%d/%Y',),
    )
    def test_default_value(self):
        session_key = 'banktransactionanalytictrendtimeform'

        form = self.app.get(self.url, user='owner').form
        self.assertEqual(form['chart'].value, TrendtimeForm.CHART_LINE)
        self.assertEqual(form['granularity'].value, GRANULARITY_MONTH)
        # Cannot mock built-in Python.
        self.assertEqual(form['date'].value, datetime.date.today().strftime('%m/%d/%Y'))
        self.assertEqual(form['reconciled'].value, '1')

        fields = {
            'chart': TrendtimeForm.CHART_BAR,
            'granularity': GRANULARITY_WEEK,
            'date': '2015-06-18',
            'reconciled': '2',
        }
        for name, value in fields.items():
            form[name] = value
        response = form.submit('filter').maybe_follow()
        form = response.form
        self.assertEqual(fields['chart'], form['chart'].value)
        self.assertEqual(fields['granularity'], form['granularity'].value)
        self.assertEqual(
            str(datetime.date(2015, 6, 18)),
            form['date'].value,
        )
        self.assertDictEqual(
            self.app.session[session_key]['filters']['date_kwargs'],
            {
                'year': 2015,
                'month': 6,
                'day': 18,
            },
        )
        self.assertEqual(fields['reconciled'], form['reconciled'].value)

        # Test manual reset
        form['chart'] = TrendtimeForm.CHART_LINE
        form['granularity'] = GRANULARITY_MONTH
        form['reconciled'] = '1'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(response.status_code, 200)
        form = response.form
        self.assertEqual(form['chart'].value, TrendtimeForm.CHART_LINE)
        self.assertEqual(form['granularity'].value, GRANULARITY_MONTH)
        self.assertEqual(form['reconciled'].value, '1')

    @override_settings(
        LANGUAGE_CODE='fr-fr',
        DATETIME_INPUT_FORMATS=('%d/%m/%Y',),
        DECIMAL_SEPARATOR=',',
    )
    def test_default_value_localize(self):

        session_key = 'banktransactionanalytictrendtimeform'

        form = self.app.get(self.url, user='owner').form
        self.assertEqual(form['date'].value, datetime.date.today().strftime('%d/%m/%Y'))

        form['date'] = '18/06/2015'
        response = form.submit('filter').maybe_follow()
        form = response.form

        self.assertEqual(form['date'].value, '18/06/2015')
        self.assertDictEqual(
            self.app.session[session_key]['filters']['date_kwargs'],
            {
                'year': 2015,
                'month': 6,
                'day': 18,
            },
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_reset(self):

        form = self.app.get(self.url, user='owner').form
        form = form.submit('reset').maybe_follow().form

        fields = {
            'chart': TrendtimeForm.CHART_BAR,
            'granularity': GRANULARITY_WEEK,
            'date': '2015-06-18',
            'reconciled': '2',
        }
        for name, value in fields.items():
            form[name] = value
        form.submit('filter').maybe_follow()
        form.submit('reset').maybe_follow()

        form = self.app.get(self.url, user='owner').form
        self.assertEqual(form['chart'].value, TrendtimeForm.CHART_LINE)
        self.assertEqual(form['granularity'].value, GRANULARITY_MONTH)
        self.assertEqual(form['date'].value, datetime.date.today().strftime('%m/%d/%Y'))
        self.assertEqual(form['reconciled'].value, '1')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_success_url(self):

        form = self.app.get(self.url, user='owner').form
        form['date'] = '2015-06-18'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(self.url, response.request.path)

        response = response.form.submit('reset').maybe_follow()
        self.assertEqual(self.url, response.request.path)

    @override_settings(LANGUAGE_CODE='en-us')
    def test_queryset_balance(self):

        bankaccount = BankAccountFactory(owners=[self.owner])
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        # No filter.
        response = self.app.get(url, user='owner')
        self.assertNotIn('balance_initial', response.context)

        # No ones.
        form = response.form
        form['date'] = '2015-06-05'
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('balance_initial', response.context)

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-05-13',
            reconciled=True,
        )

        form = response.form
        form['date'] = '2015-05-20'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['balance_initial'],
            0,
        )

        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('165.23'),
            date='2015-05-13',
            reconciled=True,
        )

        # Not reconciled
        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-05-14',
        )

        # Another bank account
        bt4 = BankTransactionFactory(  # noqa
            bankaccount=BankAccountFactory(),
            amount=Decimal('-654.12'),
            date='2015-05-14',
            reconciled=True,
        )

        # Current, not previous
        bt5 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-06-14',
        )
        bt6 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-06-14',
            reconciled=True,
        )

        # Inactive
        bt7 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-05-14',
            status=BankTransaction.STATUS_INACTIVE,
        )

        # Ignored
        bt8 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-05-14',
            status=BankTransaction.STATUS_IGNORED,
        )

        form = response.form
        form['date'] = '2015-06-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['balance_initial'],
            bt1.amount + bt2.amount + bt3.amount,
        )

        form = response.form
        form['date'] = '2015-06-05'
        form['granularity'] = GRANULARITY_MONTH
        form['reconciled'] = '2'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['balance_initial'],
            bt1.amount + bt2.amount,
        )

        form = response.form
        form['date'] = '2015-06-05'
        form['granularity'] = GRANULARITY_MONTH
        form['reconciled'] = '3'
        response = form.submit('filter').maybe_follow()
        self.assertEqual(
            response.context['balance_initial'],
            bt3.amount,
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_queryset_items(self):

        bankaccount = BankAccountFactory(owners=[self.owner])
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        response = self.app.get(url, user='owner')

        form = response.form
        form['date'] = '2015-06-20'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertNotIn('chart_data', response.context)

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-06-02',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-45.40'),
            date='2015-06-03',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('150.23'),
            date='2015-06-03',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-10.79'),
            date='2015-06-05',
            reconciled=True,
        )

        # Not reconciled
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-69.00'),
            date='2015-06-05',
        )

        # Other bank account.
        BankTransactionFactory(
            bankaccount=BankAccountFactory(),
            amount=Decimal('-39.90'),
            date='2015-06-05',
            reconciled=True,
        )

        # Inactive
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-19.90'),
            date='2015-06-05',
            reconciled=True,
            status=BankTransaction.STATUS_INACTIVE,
        )

        # Ignored
        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-19.90'),
            date='2015-06-05',
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
        )

        form = response.form
        form['date'] = '2015-06-15'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertListEqual(
            response.context['rows'],
            [
                {
                    'date': datetime.date(2015, 6, 2),
                    'balance': Decimal('-15.40'),
                    'delta': Decimal('-15.40'),
                    'percentage': 0,
                },
                {
                    'date': datetime.date(2015, 6, 3),
                    'balance': Decimal('89.43'),
                    'delta': Decimal('104.83'),
                    'percentage': Decimal('-680.71'),
                },
                {
                    'date': datetime.date(2015, 6, 4),
                    'balance': Decimal('89.43'),
                    'delta': 0,
                    'percentage': 0,
                },
                {
                    'date': datetime.date(2015, 6, 5),
                    'balance': Decimal('9.64'),
                    'delta': Decimal('-79.79'),
                    'percentage': Decimal('-89.22'),
                },
            ],
        )
        self.assertListEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'],
            [-15.40, 89.43, 89.43, 9.64],
        )

        # Reconciled
        form = response.form
        form['date'] = '2015-06-15'
        form['reconciled'] = '2'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertListEqual(
            response.context['rows'],
            [
                {
                    'date': datetime.date(2015, 6, 2),
                    'balance': Decimal('-15.40'),
                    'delta': Decimal('-15.40'),
                    'percentage': 0,
                },
                {
                    'date': datetime.date(2015, 6, 3),
                    'balance': Decimal('89.43'),
                    'delta': Decimal('104.83'),
                    'percentage': Decimal('-680.71'),
                },
                {
                    'date': datetime.date(2015, 6, 4),
                    'balance': Decimal('89.43'),
                    'delta': 0,
                    'percentage': 0,
                },
                {
                    'date': datetime.date(2015, 6, 5),
                    'balance': Decimal('78.64'),
                    'delta': Decimal('-10.79'),
                    'percentage': Decimal('-12.07'),
                },
            ],
        )
        self.assertListEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'],
            [-15.40, 89.43, 89.43, 78.64],
        )

        # Not reconciled
        form = response.form
        form['date'] = '2015-06-15'
        form['reconciled'] = '3'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertListEqual(
            response.context['rows'],
            [
                {
                    'date': datetime.date(2015, 6, 5),
                    'balance': Decimal('-69.00'),
                    'delta': Decimal('-69.00'),
                    'percentage': 0,
                },
            ],
        )
        self.assertListEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'],
            [-69.00],
        )
        response = form.submit('reset').maybe_follow()

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.79'),
            date='2015-05-30',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('236.78'),
            date='2015-07-02',
            reconciled=True,
        )

        form = response.form
        form['date'] = '2015-06-15'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertDictEqual(
            response.context['rows'][0],
            {
                'date': datetime.date(2015, 6, 1),
                'balance': Decimal('-15.79'),
                'delta': 0,
                'percentage': 0,
            },
        )
        self.assertDictEqual(
            response.context['rows'][5],
            {
                'date': datetime.date(2015, 6, 6),
                'balance': Decimal('-6.15'),
                'delta': 0,
                'percentage': 0,
            },
        )
        self.assertDictEqual(
            response.context['rows'][6],
            {
                'date': datetime.date(2015, 6, 7),
                'balance': Decimal('-6.15'),
                'delta': 0,
                'percentage': 0,
            },
        )
        self.assertEqual(len(response.context['rows']), 30)
        self.assertEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'][0],
            -15.79,
        )
        self.assertEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'][5],
            -6.15,
        )
        self.assertEqual(
            json.loads(response.context['chart_data'])['data']['datasets'][0]['data'][6],
            -6.15,
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_queryset_date_range(self):

        bankaccount = BankAccountFactory(owners=[self.owner])
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        # No filter.
        response = self.app.get(url, user='owner')

        # No ones exists yet.
        form = response.form
        form['date'] = '2015-02-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertContains(
            response,
            'There is no result corresponding to your search.',
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-06-13',
            reconciled=True,
        )

        # No ones before.
        form = response.form
        form['date'] = '2015-05-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertContains(
            response,
            'There is no result corresponding to your search.',
        )

        # Yes for the current.
        form = response.form
        form['date'] = '2015-06-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertIn('rows', response.context)
        self.assertNotContains(
            response,
            'There is no result corresponding to your search.',
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-04-13',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-03-13',
        )

        BankTransactionFactory(
            bankaccount=BankAccountFactory(),
            amount=Decimal('-15.40'),
            date='2015-02-13',
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-02-13',
            status=BankTransaction.STATUS_INACTIVE,
            reconciled=True,
        )

        BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-02-13',
            status=BankTransaction.STATUS_IGNORED,
            reconciled=True,
        )

        # No ones before.
        form = response.form
        form['date'] = '2015-02-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertContains(
            response,
            'There is no result corresponding to your search.',
        )

        # Having one in same granularity.
        form = response.form
        form['date'] = '2015-03-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertIn('rows', response.context)
        self.assertNotContains(
            response,
            'There is no result corresponding to your search.',
        )

        # No one reconciled
        form = response.form
        form['date'] = '2015-03-25'
        form['granularity'] = GRANULARITY_MONTH
        form['reconciled'] = '2'
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertContains(
            response,
            'There is no result corresponding to your search.',
        )

        # Got one (not reconciled)
        form = response.form
        form['date'] = '2015-03-05'
        form['granularity'] = GRANULARITY_MONTH
        form['reconciled'] = '3'
        response = form.submit('filter').maybe_follow()
        self.assertIn('rows', response.context)
        self.assertNotContains(
            response,
            'There is no result corresponding to your search.',
        )

        # No one available next.
        form = response.form.submit('reset').maybe_follow().form
        form['date'] = '2015-07-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertNotIn('rows', response.context)
        self.assertContains(
            response,
            'There is no result corresponding to your search.',
        )

        # No one exists, but having before AND after.
        form = response.form.submit('reset').maybe_follow().form
        form['date'] = '2015-05-05'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertIn('rows', response.context)
        self.assertNotContains(
            response,
            'There is no result corresponding to your search.',
        )

    def test_monthly_paginator(self):

        bankaccount = BankAccountFactory(balance=0, owners=[self.owner])
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        BankTransactionFactory(bankaccount=bankaccount, date='2015-06-15')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-06-25')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-15')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-15')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-08-15')

        response = self.app.get(url, user='owner')
        form = response.form
        form['date'] = '2015-06-02'
        form['granularity'] = GRANULARITY_MONTH
        response = form.submit('filter').maybe_follow()
        self.assertEqual(len(response.context[0]['rows']), 16)
        self.assertEqual(
            response.context[0]['page_obj'].paginator.date_min,
            datetime.date(2015, 6, 1),
        )
        self.assertEqual(
            response.context[0]['page_obj'].paginator.date_max,
            datetime.date(2015, 8, 31),
        )
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 6, 2),
        )

        pager_prev_url = url + '?date=2015-05-01'
        with self.assertRaises(IndexError):
            response.click(href=pager_prev_url)

        pager_next_url = '\?date=2015-07-01'
        response = response.click(href=pager_next_url)
        self.assertEqual(len(response.context[0]['rows']), 31)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 7, 1),
        )
        self.assertEqual(
            response.form['date'].value,
            '2015-06-02',
        )

        pager_next_url = '\?date=2015-08-01'
        response = response.click(href=pager_next_url)
        self.assertEqual(len(response.context[0]['rows']), 15)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 8, 1),
        )

        pager_next_url = '\?date=2015-09-01'
        with self.assertRaises(IndexError):
            response.click(href=pager_next_url)

        # Try to insert a fake date manually. Date filter should be used
        # instead.
        response = self.app.get(url + '?date=foo', user='owner')
        self.assertEqual(len(response.context[0]['rows']), 16)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 6, 2),
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_weekly_paginator(self):

        bankaccount = BankAccountFactory(balance=0, owners=[self.owner])
        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })

        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-14')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-16')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-21')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-21')
        BankTransactionFactory(bankaccount=bankaccount, date='2015-07-29')

        response = self.app.get(url, user='owner')
        form = response.form
        form['date'] = '2015-07-13'
        form['granularity'] = GRANULARITY_WEEK
        response = form.submit('filter').maybe_follow()
        self.assertEqual(len(response.context[0]['rows']), 5)
        self.assertEqual(
            response.context[0]['page_obj'].paginator.date_min,
            datetime.date(2015, 7, 12),
        )
        self.assertEqual(
            response.context[0]['page_obj'].paginator.date_max,
            datetime.date(2015, 8, 1),
        )
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 7, 13),
        )

        pager_prev_url = url + '?date=2015-07-05'
        with self.assertRaises(IndexError):
            response.click(href=pager_prev_url)

        pager_next_url = '\?date=2015-07-19'
        response = response.click(href=pager_next_url)
        self.assertEqual(len(response.context[0]['rows']), 7)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 7, 19),
        )
        self.assertEqual(
            response.form['date'].value,
            '2015-07-13',
        )

        pager_next_url = '\?date=2015-07-26'
        response = response.click(href=pager_next_url)
        self.assertEqual(len(response.context[0]['rows']), 4)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 7, 26),
        )

        pager_next_url = '\?date=2015-08-02'
        with self.assertRaises(IndexError):
            response.click(href=pager_next_url)

        # Try to insert a fake date manually. Date filter should be used
        # instead.
        response = self.app.get(url + '?date=foo', user='owner')
        self.assertEqual(len(response.context[0]['rows']), 5)
        self.assertEqual(
            response.context[0]['page_obj'].date,
            datetime.date(2015, 7, 13),
        )


class TrendtimeSummaryViewTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
        ]

    @override_settings(LANGUAGE_CODE='en-us')
    def test_queryset(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url_form = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })
        url_summary = reverse('banktransactionanalytics:trendtimesummary', kwargs={
            'bankaccount_pk': bankaccount.pk,
            'year': '2015',
            'month': '6',
            'day': '15',
        })

        # Test without bank transactions and init filters.
        form = self.app.get(url_form, user='owner').form
        form['date'] = '2015-06-01'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertIn('banktransactions', response.context)
        self.assertFalse(response.context['banktransactions'])

        # Test with dummy date.
        response = self.app.get(
            reverse('banktransactionanalytics:trendtimesummary', kwargs={
                'bankaccount_pk': bankaccount.pk,
                'year': '9999',
                'month': '99',
                'day': '99',
            }),
            user='owner',
        )
        self.assertIn('banktransactions', response.context)
        self.assertFalse(response.context['banktransactions'])

        # Test with invalid date.
        response = self.app.get(
            reverse('banktransactionanalytics:trendtimesummary', kwargs={
                'bankaccount_pk': bankaccount.pk,
                'year': '2015',
                'month': '2',
                'day': '31',
            }),
            user='owner',
        )
        self.assertIn('banktransactions', response.context)
        self.assertFalse(response.context['banktransactions'])

        bt1 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-15.40'),
            date='2015-06-15',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        bt2 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('165.23'),
            date='2015-06-15',
            reconciled=True,
            tag=self.banktransactiontags[0],
        )

        # Not reconciled.
        bt3 = BankTransactionFactory(
            bankaccount=bankaccount,
            amount=Decimal('-654.12'),
            date='2015-06-15',
            tag=self.banktransactiontags[1],
        )

        # Too late
        bt4 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-134.00'),
            date='2015-12-16',
            reconciled=False,
        )

        # Other bank account
        bt5 = BankTransactionFactory(  # noqa
            bankaccount=BankAccountFactory(),
            amount=Decimal('-45.88'),
            date='2015-06-15',
            reconciled=True,
        )

        # Inactive
        bt6 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_INACTIVE,
        )

        # Ignored
        bt7 = BankTransactionFactory(  # noqa
            bankaccount=bankaccount,
            amount=Decimal('-88.54'),
            date='2015-06-15',
            reconciled=True,
            status=BankTransaction.STATUS_IGNORED,
        )

        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt1), repr(bt2), repr(bt3)],
        )

        response = form.submit('reset').maybe_follow()
        form = response.form
        form['date'] = '2012-06-15'
        form['reconciled'] = '2'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt1), repr(bt2)],
        )

        response = form.submit('reset').maybe_follow()
        form = response.form
        form['date'] = '2012-06-15'
        form['reconciled'] = '3'
        form.submit('filter').maybe_follow()
        response = self.app.get(url_summary, user='owner')
        self.assertQuerysetEqual(
            response.context['banktransactions'],
            [repr(bt3)],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_ajax(self):

        bankaccount = BankAccountFactory(owners=[self.owner])

        url_form = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': bankaccount.pk
        })
        url_summary = reverse('banktransactionanalytics:trendtimesummary', kwargs={
            'bankaccount_pk': bankaccount.pk,
            'year': '2015',
            'month': '6',
            'day': '15',
        })

        form = self.app.get(url_form, user='owner').form
        form['date'] = '2015-06-01'
        form.submit('filter').maybe_follow()

        response = self.app.get(url_summary, user='owner', xhr=False)
        self.assertContains(
            response,
            "{bankaccount}'s trendtime statistics summary".format(bankaccount=bankaccount),
        )

        response = self.app.get(url_summary, user='owner', xhr=True)
        self.assertNotContains(
            response,
            "{bankaccount}'s trendtime statistics summary".format(bankaccount=bankaccount),
        )
