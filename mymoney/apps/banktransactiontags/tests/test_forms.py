from django.contrib import messages
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import ugettext as _

from django_webtest import WebTest

from mymoney.apps.banktransactiontags.factories import (
    BankTransactionTagFactory,
)
from mymoney.core.factories import UserFactory

from ..models import BankTransactionTag


class FormTestCase(WebTest):

    @classmethod
    def setUpTestData(cls):
        cls.superowner = UserFactory(username='superowner', user_permissions='admin')

    @override_settings(LANGUAGE_CODE='en-us')
    def test_create_form(self):

        url = reverse('banktransactiontags:create')
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('owner', form.fields)

        form['name'] = 'test'
        response = form.submit().maybe_follow()

        banktransactiontag = BankTransactionTag.objects.get(name='test')
        self.assertEqual(banktransactiontag.owner.pk, self.superowner.pk)

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction tag %(name)s was created successfully.' % {
                'name': banktransactiontag.name
            },
            [message.message for message in storage],
        )

    @override_settings(LANGUAGE_CODE='en-us')
    def test_update_form(self):

        banktransactiontag = BankTransactionTagFactory(owner=self.superowner)

        url = reverse('banktransactiontags:update', kwargs={
            'pk': banktransactiontag.pk
        })
        form = self.app.get(url, user='superowner').form

        self.assertNotIn('owner', form.fields)

        form['name'] = 'rename'
        response = form.submit().maybe_follow()

        banktransactiontag.refresh_from_db()
        self.assertEqual(banktransactiontag.name, 'rename')
        self.assertEqual(banktransactiontag.owner.pk, self.superowner.pk)

        storage = messages.get_messages(response.context[0].request)
        self.assertIn(
            'Bank transaction tag %(name)s was updated successfully.' % {
                'name': banktransactiontag.name
            },
            [message.message for message in storage],
        )

    def test_delete_form(self):

        banktransactiontag = BankTransactionTagFactory(owner=self.superowner)

        url = reverse('banktransactiontags:delete', kwargs={
            'pk': banktransactiontag.pk
        })

        response = self.app.get(url, user='superowner')
        response = response.click(description=_('Cancel'))
        self.assertEqual(response.request.path, reverse('banktransactiontags:list'))
        banktransactiontag.refresh_from_db()

        response = (self.app.get(url, user='superowner')
                    .form.submit()
                    .maybe_follow())
        self.assertEqual(response.request.path, reverse('banktransactiontags:list'))
        with self.assertRaises(BankTransactionTag.DoesNotExist):
            banktransactiontag.refresh_from_db()

    def test_redirect_form(self):

        # Check on create form.
        url = reverse('banktransactiontags:create')
        form = self.app.get(url, user='superowner').form
        self.assertFalse(form['redirect'].checked)
        edit = {
            'name': 'test redirect',
            'redirect': True,
        }
        for name, value in edit.items():
            form[name] = value
        response = form.submit()
        self.assertRedirects(response, url + '?self-redirect=1')
        response = response.maybe_follow()
        self.assertTrue(response.form['redirect'].checked)

        # Not on update form.
        banktransactiontag = BankTransactionTagFactory(owner=self.superowner)

        url = reverse('banktransactiontags:update', kwargs={
            'pk': banktransactiontag.pk
        })
        form = self.app.get(url, user='superowner').form
        self.assertNotIn('redirect', form.fields)
