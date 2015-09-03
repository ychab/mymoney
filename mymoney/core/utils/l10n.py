from django.utils.translation import get_language


def get_language_upper(lang=None):
    lang = lang if lang else get_language()
    if lang.find('-') >= 0:
        lang = lang[:2].lower() + '-' + lang[3:].upper()
    return lang
