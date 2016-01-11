from decimal import Decimal

from django.test import SimpleTestCase

from mymoney.core.utils.currencies import format_currency


class CurrencyFormatTestCase(SimpleTestCase):

    def test_format_currency(self):

        with self.settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(
                format_currency(Decimal('-1547.23'), 'USD'),
                "-$1,547.23",
            )

        with self.settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(
                format_currency(Decimal('-1547.23'), 'EUR'),
                '-1\xa0547,23\xa0€',
            )

        with self.settings(LANGUAGE_CODE='fr'):
            self.assertEqual(
                format_currency(-1547, 'EUR'),
                "-1\xa0547,00\xa0€",
            )

        with self.settings(LANGUAGE_CODE='it'):
            self.assertEqual(
                format_currency(-1547, 'EUR'),
                "-1.547,00\xa0€",
            )
