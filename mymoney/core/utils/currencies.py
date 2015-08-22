import operator

from django.utils.formats import get_format
from django.utils.translation import get_language

from babel import numbers
from babel.core import Locale


def get_currencies():
    """
    Returns a list of currencies.
    """
    return sorted(
        Locale.default().currencies.items(),
        key=operator.itemgetter(1)
    )


def format_currency(amount, currency):
    """
    Format an amount with the currency given for the current active language.
    """
    try:
        format = get_format('CURRENCY_PATTERN_FORMAT')
    except AttributeError:
        format = None
    lang = get_language()
    locale = lang[:2] + ('_' + lang[3:].upper() if len(lang) > 2 else '')

    return numbers.format_currency(
        amount, currency, format=format, locale=locale
    )
