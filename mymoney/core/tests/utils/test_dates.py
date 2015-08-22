import datetime
import unittest

from django.test import override_settings, SimpleTestCase

from mymoney.core.utils.dates import (
    get_date_ranges, get_datetime_ranges, get_weekday, GRANULARITY_MONTH,
    GRANULARITY_WEEK,
)


class DateUtilsTestCase(unittest.TestCase):

    def test_weekday(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            self.assertEqual(get_weekday(), 6)

        with override_settings(LANGUAGE_CODE='fr-fr'):
            self.assertEqual(get_weekday(), 0)

        with override_settings(LANGUAGE_CODE='fa'):
            self.assertEqual(get_weekday(), 5)


class DateRangesTestCase(SimpleTestCase):

    def test_week(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            s, e = get_date_ranges(
                datetime.date(2015, 4, 29), GRANULARITY_WEEK
            )
            self.assertEqual(s, datetime.date(2015, 4, 26))
            self.assertEqual(e, datetime.date(2015, 5, 2))

        with override_settings(LANGUAGE_CODE='fr-fr'):
            s, e = get_date_ranges(
                datetime.date(2015, 4, 29), GRANULARITY_WEEK
            )
            self.assertEqual(s, datetime.date(2015, 4, 27))
            self.assertEqual(e, datetime.date(2015, 5, 3))

        with override_settings(LANGUAGE_CODE='fr-fr'):
            s, e = get_date_ranges(
                datetime.date(2015, 7, 13), GRANULARITY_WEEK
            )
            self.assertEqual(s, datetime.date(2015, 7, 13))
            self.assertEqual(e, datetime.date(2015, 7, 19))

        with override_settings(LANGUAGE_CODE='fa'):
            s, e = get_date_ranges(
                datetime.date(2015, 4, 29), GRANULARITY_WEEK
            )
            self.assertEqual(s, datetime.date(2015, 4, 25))
            self.assertEqual(e, datetime.date(2015, 5, 1))

    def test_month(self):

        s, e = get_date_ranges(
            datetime.date(2015, 2, 15), GRANULARITY_MONTH
        )
        self.assertEqual(s, datetime.date(2015, 2, 1))
        self.assertEqual(e, datetime.date(2015, 2, 28))

        s, e = get_date_ranges(
            datetime.date(2016, 2, 15), GRANULARITY_MONTH
        )
        self.assertEqual(s, datetime.date(2016, 2, 1))
        self.assertEqual(e, datetime.date(2016, 2, 29))


class DatetimeRangesTestCase(SimpleTestCase):

    def test_week(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            s, e = get_datetime_ranges(
                datetime.datetime(2015, 4, 29, 15, 4),
                GRANULARITY_WEEK,
            )
            self.assertEqual(s, datetime.datetime(2015, 4, 26, 0, 0, 0, 0))
            self.assertEqual(e, datetime.datetime(2015, 5, 2, 23, 59, 59, 0))

        with override_settings(LANGUAGE_CODE='fr-fr'):
            s, e = get_datetime_ranges(
                datetime.datetime(2015, 4, 29, 17, 55),
                GRANULARITY_WEEK,
            )
            self.assertEqual(s, datetime.datetime(2015, 4, 27, 0, 0, 0, 0))
            self.assertEqual(e, datetime.datetime(2015, 5, 3, 23, 59, 59, 0))

        with override_settings(LANGUAGE_CODE='fr-fr'):
            s, e = get_datetime_ranges(
                datetime.datetime(2015, 7, 13, 17, 14), GRANULARITY_WEEK
            )
            self.assertEqual(s, datetime.datetime(2015, 7, 13, 0, 0, 0, 0))
            self.assertEqual(e, datetime.datetime(2015, 7, 19, 23, 59, 59, 0))

    def test_month(self):

        s, e = get_datetime_ranges(
            datetime.datetime(2015, 2, 15, 12, 15),
            GRANULARITY_MONTH,
        )
        self.assertEqual(s, datetime.datetime(2015, 2, 1, 0, 0, 0, 0))
        self.assertEqual(e, datetime.datetime(2015, 2, 28, 23, 59, 59, 0))

        s, e = get_datetime_ranges(
            datetime.datetime(2016, 2, 15, 12, 15),
            GRANULARITY_MONTH,
        )
        self.assertEqual(s, datetime.datetime(2016, 2, 1, 0, 0, 0, 0))
        self.assertEqual(e, datetime.datetime(2016, 2, 29, 23, 59, 59, 0))
