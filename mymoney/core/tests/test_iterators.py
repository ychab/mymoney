import datetime
import unittest

from ..iterators import DateIterator


class DateIteratorTestCase(unittest.TestCase):

    def test_iterator(self):

        iterator = DateIterator(
            datetime.date(2015, 2, 25),
            datetime.date(2015, 3, 2),
        )

        iter(iterator)
        self.assertEqual(next(iterator), datetime.date(2015, 2, 25))
        self.assertEqual(next(iterator), datetime.date(2015, 2, 26))
        self.assertEqual(next(iterator), datetime.date(2015, 2, 27))
        self.assertEqual(next(iterator), datetime.date(2015, 2, 28))
        self.assertEqual(next(iterator), datetime.date(2015, 3, 1))
        self.assertEqual(next(iterator), datetime.date(2015, 3, 2))
        with self.assertRaises(StopIteration):
            next(iterator)

        day = 25
        month = 2
        for date_step in iterator:
            self.assertEqual(date_step, datetime.date(2015, month, day))
            day += 1

            if day == 29:
                day = 1
                month += 1
