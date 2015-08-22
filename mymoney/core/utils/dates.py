import datetime

from django.utils.formats import get_format
from django.utils.timezone import make_aware

from dateutil.relativedelta import relativedelta, weekday

GRANULARITY_MONTH = 'month'
GRANULARITY_WEEK = 'week'


def get_weekday():
    """
    Returns the ISO first day of the week for the current locale.
    Weekday expect Monday as 0, whereas FIRST_DAY_OF_WEEK use Sunday as 0.
    """
    first_day = get_format('FIRST_DAY_OF_WEEK')
    return first_day - 1 if first_day > 0 else 6


def get_datetime_ranges(base_datetime, granularity):
    """
    Returns a datetime ranges for the given granularity based on the given
    datetime.

    :param base_datetime: a datetime to deduce range
    :param granularity: the type of range to deduce
    :return: tuple, a datetime ranges
    """
    start = end = None

    if granularity == GRANULARITY_WEEK:
        week_day = get_weekday()
        start = base_datetime + relativedelta(
            weekday=weekday(week_day, n=-1), hour=0, minute=0, second=0,
            microsecond=0,
        )
        end = base_datetime + relativedelta(
            weekday=weekday(week_day, n=-1), weeks=1, hour=0, minute=0,
            second=0, microsecond=0,
        )
        # Cannot use it above because day is not changed. Another way?
        end += relativedelta(seconds=-1)

    elif granularity == GRANULARITY_MONTH:  # pragma: no branch
        start = base_datetime + relativedelta(
            day=1, hour=0, minute=0, second=0, microsecond=0,
        )
        end = base_datetime + relativedelta(
            months=1, seconds=-1, day=1, hour=0, minute=0, second=0,
            microsecond=0,
        )

    return start, end


def get_date_ranges(base_date, granularity):
    """
    Returns a date ranges for the given granularity based on the given date.

    :param base_date: a date to deduce range
    :param granularity: the type of range to deduce
    :return: tuple, a date ranges
    """
    start, end = get_datetime_ranges(
        make_aware(datetime.datetime.combine(base_date, datetime.time())),
        granularity,
    )

    return start.date(), end.date()
