from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactiontags.factories import \
    BankTransactionTagFactory
from mymoney.core.factories import UserFactory


class RatioFormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])
        cls.banktransactiontags = [
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
            BankTransactionTagFactory(owner=cls.owner),
        ]

    def test_fields(self):

        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='owner').form
        self.assertListEqual(
            sorted([int(option[0]) for option in form['tags'].options]),
            [obj.pk for obj in self.banktransactiontags],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_field_required(self):

        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='owner').form
        response = form.submit('filter').maybe_follow()
        self.assertFormError(response, 'form', 'date_start', [
            'This field is required.',
        ])
        self.assertFormError(response, 'form', 'date_end', [
            'This field is required.',
        ])

    @override_settings(LANGUAGE_CODE='en-us')
    def test_clean(self):

        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='owner').form
        form['date_start'] = '2015-05-11'
        form['date_end'] = '2015-05-10'
        response = form.submit('filter').maybe_follow()
        self.assertFormError(
            response,
            'form',
            None,
            ['Date start could not be greater than date end.'],
        )

        form = self.app.get(url, user='owner').form
        form['sum_min'] = 200
        form['sum_max'] = 100
        response = form.submit('filter').maybe_follow()
        self.assertFormError(
            response,
            'form',
            None,
            ['Minimum sum could not be greater than maximum sum.'],
        )


class TrendtimeFormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner])

    @override_settings(LANGUAGE_CODE='en-us')
    def test_field_required(self):

        url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

        form = self.app.get(url, user='owner').form
        form['date'] = ''
        response = form.submit('filter').maybe_follow()
        self.assertFormError(response, 'form', 'date', [
            'This field is required.',
        ])
