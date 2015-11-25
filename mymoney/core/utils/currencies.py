import operator

from django.utils.translation import get_language, to_locale

from babel import numbers
from babel.core import Locale

from .formats import get_format


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
    lang = get_language()
    format = get_format('CURRENCY_PATTERN_FORMAT', lang)
    locale = to_locale(lang)

    return numbers.format_currency(
        amount, currency, format=format, locale=locale
    )
