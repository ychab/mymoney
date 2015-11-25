from django.utils.formats import get_format_modules
from django.utils.translation import get_language

CACHE_FORMAT = {}


def get_format(format_type, lang=None):
    """
    Ugly workaround to security fix of 1.8.7 django.utils.formats.get_format
    which now exclude custom formats with frozenset FORMAT_SETTINGS ...
    """
    if lang is None:
        lang = get_language()

    cache_key = (format_type, lang)
    if cache_key not in CACHE_FORMAT:

        format = None
        for module in get_format_modules(lang):
            try:
                format = getattr(module, format_type)
                break
            except AttributeError:
                continue
        CACHE_FORMAT[cache_key] = format

    return CACHE_FORMAT[cache_key]
