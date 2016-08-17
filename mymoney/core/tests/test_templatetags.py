import unittest
from decimal import Decimal
from unittest import mock

from django.urls import reverse
from django.test import SimpleTestCase
from django.utils.safestring import SafeText

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.factories import BankTransactionFactory
from mymoney.apps.banktransactions.models import BankTransaction

from ..factories import UserFactory
from ..templatetags.core_tags import (
    breadcrumb, currency_positive, display_messages, form_errors_exists,
    language_to_upper, localize_positive, localize_positive_color,
    merge_form_errors, payment_method,
)


class TemplateTagsTestCase(unittest.TestCase):

    def test_display_messages(self):

        msgs = [
            mock.Mock(tags='success'),
            mock.Mock(tags='error'),
            mock.Mock(tags='debug'),
            mock.Mock(tags=None),
        ]
        context = display_messages(msgs)

        i = 0
        for msg in context['messages']:
            if i == 0:
                self.assertEqual(msg.type, 'success')
            elif i == 1:
                self.assertEqual(msg.type, 'danger')
            elif i == 2:
                self.assertEqual(msg.type, 'info')
            else:
                self.assertIsNone(msg.type)
            i += 1

    def test_payment_method(self):

        context = payment_method(BankTransaction.PAYMENT_METHOD_CREDIT_CARD)
        self.assertIsNotNone(context)

        context = payment_method(BankTransaction.PAYMENT_METHOD_CASH)
        self.assertIsNotNone(context)

        context = payment_method(BankTransaction.PAYMENT_METHOD_TRANSFER)
        self.assertIsNotNone(context)

        context = payment_method(BankTransaction.PAYMENT_METHOD_TRANSFER_INTERNAL)
        self.assertIsNotNone(context)

        context = payment_method(BankTransaction.PAYMENT_METHOD_CHECK)
        self.assertIsNotNone(context)

    def test_breadcrumb(self):

        bankaccount = BankAccountFactory()
        kwargs = {
            "bankaccount_pk": bankaccount.pk,
        }

        request = mock.Mock(path=reverse('banktransactions:create', kwargs=kwargs))
        context = breadcrumb(request)
        self.assertListEqual(
            [reverse('banktransactions:list', kwargs=kwargs)],
            [link['href'] for link in context['links']]
        )

        banktransaction = BankTransactionFactory(bankaccount=bankaccount)
        request = mock.Mock(path=reverse('banktransactions:update', kwargs={
            'pk': banktransaction.pk,
        }))
        context = breadcrumb(request, banktransaction.bankaccount.pk)
        self.assertListEqual(
            [reverse('banktransactions:list', kwargs=kwargs)],
            [link['href'] for link in context['links']]
        )

        request = mock.Mock(path=reverse('banktransactionschedulers:create', kwargs=kwargs))
        context = breadcrumb(request)
        self.assertListEqual(
            [
                reverse('banktransactions:list', kwargs=kwargs),
                reverse('banktransactionschedulers:list', kwargs=kwargs),
            ],
            [link['href'] for link in context['links']]
        )

        banktransaction = BankTransactionFactory(bankaccount=bankaccount)
        request = mock.Mock(path=reverse('banktransactionschedulers:update', kwargs={
            'pk': banktransaction.pk,
        }))
        context = breadcrumb(request, banktransaction.bankaccount.pk)
        self.assertListEqual(
            [
                reverse('banktransactions:list', kwargs=kwargs),
                reverse('banktransactionschedulers:list', kwargs=kwargs),
            ],
            [link['href'] for link in context['links']]
        )


class TemplateTagsWebTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.owner = UserFactory(username='owner')
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')
        cls.bankaccount = BankAccountFactory(owners=[cls.owner, cls.superowner])

    def test_menu_action_links(self):

        url = reverse('bankaccounts:list')
        href = reverse('bankaccounts:create')
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

        url = reverse('banktransactiontags:list')
        href = reverse('banktransactiontags:create')
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)
        href = reverse('bankaccounts:delete', kwargs={
            'pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

        url = reverse('banktransactions:calendar', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('banktransactions:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)
        href = reverse('bankaccounts:delete', kwargs={
            'pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

        url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('banktransactionschedulers:create', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

    def test_menu_tab_links(self):

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('bankaccounts:update', kwargs={
            'pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        response = self.app.get(url, user='owner')
        with self.assertRaises(IndexError):
            response.click(href=href)

    def test_menu_item_links(self):

        url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        href = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response.click(href=href, index=1)

        url = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        href = reverse('banktransactions:calendar', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response = self.app.get(url, user='superowner')
        response.click(href=href)
        href = reverse('banktransactions:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })
        response.click(href=href, index=1)


class TemplateFiltersWebTestCase(unittest.TestCase):

    def test_merge_form_errors(self):

        form = mock.Mock(
            non_field_errors=mock.Mock(return_value=[]),
            visible_fields=mock.Mock(return_value=[]),
        )
        self.assertListEqual(merge_form_errors(form), [])

        form = mock.Mock(
            non_field_errors=mock.Mock(return_value=["foo", "bar"]),
            visible_fields=mock.Mock(return_value=[]),
        )
        self.assertListEqual(merge_form_errors(form), ["foo", "bar"])

        form = mock.Mock(
            non_field_errors=mock.Mock(return_value=[]),
            visible_fields=mock.Mock(
                return_value=[
                    mock.Mock(errors=["baz", "alpha"]),
                ]
            ),
        )
        self.assertListEqual(merge_form_errors(form), ["baz", "alpha"])

        form = mock.Mock(
            non_field_errors=mock.Mock(return_value=["foo", "bar"]),
            visible_fields=mock.Mock(
                return_value=[
                    mock.Mock(errors=["baz", "alpha"]),
                    mock.Mock(errors=["beta"]),
                    mock.Mock(errors=[]),
                ]
            ),
        )
        self.assertListEqual(
            merge_form_errors(form),
            ["foo", "bar", "baz", "alpha", "beta"]
        )

    def test_form_errors_exists(self):

        form = mock.Mock(
            non_field_errors=mock.Mock(
                return_value=mock.Mock(
                    as_data=mock.Mock(
                        return_value=[
                            mock.Mock(code='foo'),
                            mock.Mock(code='bar'),
                        ]
                    )
                )
            )
        )

        self.assertTrue(form_errors_exists(form, 'bar'))
        self.assertFalse(form_errors_exists(form, 'baz'))


class TemplateFiltersTestCase(SimpleTestCase):

    def test_language_to_upper(self):
        self.assertEqual(language_to_upper('en-us'), 'en-US')
        self.assertEqual(language_to_upper('fr-fr'), 'fr-FR')
        self.assertEqual(language_to_upper('fr'), 'fr')

    def test_currency_positive(self):

        with self.settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(
                currency_positive(Decimal('1547.23'), 'USD'),
                "+$1,547.23",
            )

        with self.settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(
                currency_positive(Decimal('1547.23'), 'EUR'),
                '+1\xa0547,23\xa0€',
            )

    def test_localize_positive(self):

        with self.settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(
                localize_positive(Decimal('15.23')),
                '+15.23',
            )

        with self.settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(
                localize_positive(Decimal('15.23')),
                '+15,23',
            )

    def test_localize_positive_color(self):

        with self.settings(LANGUAGE_CODE='en-us'):
            s = localize_positive_color(Decimal('15.23'))
            self.assertIsInstance(s, SafeText)
            self.assertEqual(s, '<p class="text-success">+15.23</p>')

            s = localize_positive_color(Decimal('-15.23'))
            self.assertIsInstance(s, SafeText)
            self.assertEqual(s, '<p class="text-danger">-15.23</p>')

        with self.settings(LANGUAGE_CODE='fr-fr'):
            s = localize_positive_color(Decimal('15.23'))
            self.assertIsInstance(s, SafeText)
            self.assertEqual(s, '<p class="text-success">+15,23</p>')

            s = localize_positive_color(Decimal('-15.23'))
            self.assertIsInstance(s, SafeText)
            self.assertEqual(s, '<p class="text-danger">-15,23</p>')
