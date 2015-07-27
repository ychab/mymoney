import unittest
from datetime import date

from django.test import override_settings, SimpleTestCase

from ..paginators import (
    DatePaginator, EmptyPage, InvalidDateRanges, UnknownGranularity
)
from ..utils.dates import GRANULARITY_MONTH, GRANULARITY_WEEK


class DatePaginatorTestCase(unittest.TestCase):

    def test_invalid_date_ranges(self):

        with self.assertRaises(InvalidDateRanges):
            DatePaginator(date(2015, 7, 16), date(2015, 7, 16), GRANULARITY_WEEK)

        with self.assertRaises(InvalidDateRanges):
            DatePaginator(date(2015, 7, 16), date(2015, 7, 15), GRANULARITY_WEEK)

    def test_unknown_granularity(self):

        with self.assertRaises(UnknownGranularity):
            DatePaginator(date(2015, 7, 15), date(2015, 7, 16), 'foo')

    def test_empty_page(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 7, 31),
            GRANULARITY_MONTH,
        )

        with self.assertRaises(EmptyPage):
            paginator.page(date(2015, 6, 30))

        with self.assertRaises(EmptyPage):
            paginator.page(date(2015, 8, 1))

        # Check that no exception are raised.
        paginator.page(date(2015, 7, 1))
        paginator.page(date(2015, 7, 31))


class MonthlyDatePageTestCase(unittest.TestCase):

    def test_has_next(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 8, 31),
            GRANULARITY_MONTH,
        )
        self.assertTrue(paginator.page(date(2015, 7, 15)).has_next())
        self.assertTrue(paginator.page(date(2015, 7, 31)).has_next())
        self.assertFalse(paginator.page(date(2015, 8, 15)).has_next())

    def test_has_previous(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 8, 31),
            GRANULARITY_MONTH,
        )
        self.assertTrue(paginator.page(date(2015, 8, 15)).has_previous())
        self.assertTrue(paginator.page(date(2015, 8, 1)).has_previous())
        self.assertFalse(paginator.page(date(2015, 7, 15)).has_previous())

    def test_has_other_pages(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 8, 31),
            GRANULARITY_MONTH,
        )
        self.assertTrue(paginator.page(date(2015, 7, 15)).has_other_pages())
        self.assertTrue(paginator.page(date(2015, 7, 31)).has_other_pages())
        self.assertTrue(paginator.page(date(2015, 8, 15)).has_other_pages())
        self.assertTrue(paginator.page(date(2015, 8, 1)).has_other_pages())

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 7, 31),
            GRANULARITY_MONTH,
        )
        self.assertFalse(paginator.page(date(2015, 7, 15)).has_other_pages())

    def test_next(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 8, 31),
            GRANULARITY_MONTH,
        )
        self.assertEqual(
            paginator.page(date(2015, 7, 15)).next_date(),
            date(2015, 8, 1)
        )
        self.assertEqual(
            paginator.page(date(2015, 7, 1)).next_date(),
            date(2015, 8, 1)
        )

    def test_previous(self):

        paginator = DatePaginator(
            date(2015, 7, 1),
            date(2015, 8, 31),
            GRANULARITY_MONTH,
        )
        self.assertEqual(
            paginator.page(date(2015, 8, 15)).previous_date(),
            date(2015, 7, 1)
        )
        self.assertEqual(
            paginator.page(date(2015, 8, 1)).previous_date(),
            date(2015, 7, 1)
        )


class WeeklyDatePageTestCase(SimpleTestCase):

    def test_has_next(self):

        with override_settings(LANGUAGE_CODE='fr-fr'):
            paginator = DatePaginator(
                date(2015, 7, 27),
                date(2015, 8, 9),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 7, 29)).has_next())
            self.assertTrue(paginator.page(date(2015, 8, 2)).has_next())
            self.assertFalse(paginator.page(date(2015, 8, 3)).has_next())

        with override_settings(LANGUAGE_CODE='en-us'):
            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 8),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 7, 28)).has_next())
            self.assertTrue(paginator.page(date(2015, 8, 1)).has_next())
            self.assertFalse(paginator.page(date(2015, 8, 2)).has_next())

    def test_has_previous(self):

        with override_settings(LANGUAGE_CODE='fr-fr'):
            paginator = DatePaginator(
                date(2015, 7, 27),
                date(2015, 8, 9),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 8, 6)).has_previous())
            self.assertTrue(paginator.page(date(2015, 8, 3)).has_previous())
            self.assertFalse(paginator.page(date(2015, 8, 2)).has_previous())

        with override_settings(LANGUAGE_CODE='en-us'):
            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 8),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 8, 5)).has_previous())
            self.assertTrue(paginator.page(date(2015, 8, 2)).has_previous())
            self.assertFalse(paginator.page(date(2015, 8, 1)).has_previous())

    def test_has_other_pages(self):

        with override_settings(LANGUAGE_CODE='fr-fr'):
            paginator = DatePaginator(
                date(2015, 7, 27),
                date(2015, 8, 16),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 8, 6)).has_other_pages())
            self.assertTrue(paginator.page(date(2015, 7, 29)).has_other_pages())
            self.assertTrue(paginator.page(date(2015, 8, 13)).has_other_pages())

            paginator = DatePaginator(
                date(2015, 7, 27),
                date(2015, 8, 2),
                GRANULARITY_WEEK,
            )
            self.assertFalse(paginator.page(date(2015, 7, 29)).has_other_pages())

        with override_settings(LANGUAGE_CODE='en-us'):
            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 15),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 8, 5)).has_other_pages())
            self.assertTrue(paginator.page(date(2015, 7, 28)).has_other_pages())
            self.assertTrue(paginator.page(date(2015, 8, 12)).has_other_pages())

            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 1),
                GRANULARITY_WEEK,
            )
            self.assertFalse(paginator.page(date(2015, 7, 28)).has_other_pages())

    def test_next(self):

        with override_settings(LANGUAGE_CODE='fr-fr'):
            paginator = DatePaginator(
                date(2015, 7, 20),
                date(2015, 8, 9),
                GRANULARITY_WEEK,
            )
            self.assertEqual(
                paginator.page(date(2015, 7, 29)).next_date(),
                date(2015, 8, 3)
            )
            self.assertEqual(
                paginator.page(date(2015, 7, 27)).next_date(),
                date(2015, 8, 3)
            )

        with override_settings(LANGUAGE_CODE='en-us'):
            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 8),
                GRANULARITY_WEEK,
            )
            self.assertTrue(paginator.page(date(2015, 7, 28)).has_next())
            self.assertTrue(paginator.page(date(2015, 8, 1)).has_next())
            self.assertFalse(paginator.page(date(2015, 8, 2)).has_next())

    def test_previous(self):

        with override_settings(LANGUAGE_CODE='fr-fr'):
            paginator = DatePaginator(
                date(2015, 7, 27),
                date(2015, 8, 9),
                GRANULARITY_WEEK,
            )
            self.assertEqual(
                paginator.page(date(2015, 8, 9)).previous_date(),
                date(2015, 7, 27),
            )
            self.assertEqual(
                paginator.page(date(2015, 8, 3)).previous_date(),
                date(2015, 7, 27),
            )

        with override_settings(LANGUAGE_CODE='en-us'):
            paginator = DatePaginator(
                date(2015, 7, 26),
                date(2015, 8, 8),
                GRANULARITY_WEEK,
            )
            self.assertEqual(
                paginator.page(date(2015, 8, 8)).previous_date(),
                date(2015, 7, 26),
            )
            self.assertEqual(
                paginator.page(date(2015, 8, 2)).previous_date(),
                date(2015, 7, 26),
            )
