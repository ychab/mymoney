import unittest
from decimal import Decimal
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import override_settings, SimpleTestCase

from django_webtest import WebTest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.apps.banktransactions.models import BankTransaction

from ..factories import UserFactory
from ..templatetags.core_tags import (
    currency_positive, display_messages, form_errors_exists, localize_positive,
    merge_form_errors, payment_method
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

    def test_currency_positive(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(
                currency_positive(Decimal('1547.23'), 'USD'),
                "+$1,547.23",
            )

        with override_settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(
                currency_positive(Decimal('1547.23'), 'EUR'),
                '+1\xa0547,23\xa0€',
            )

    def test_localize_positive(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(
                localize_positive(Decimal('15.23')),
                '+15.23',
            )

        with override_settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(
                localize_positive(Decimal('15.23')),
                '+15,23',
            )
