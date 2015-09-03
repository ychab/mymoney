from django.test import SimpleTestCase

from ...utils.l10n import get_language_upper


class UtilsTestCase(SimpleTestCase):

    def test_language_upper(self):

        with self.settings(LANGUAGE_CODE='fr'):
            self.assertEqual(get_language_upper(), 'fr')

        with self.settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(get_language_upper(), 'fr-FR')
            self.assertEqual(get_language_upper('en-us'), 'en-US')
