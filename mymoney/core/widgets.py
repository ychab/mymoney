from django.conf import settings
from django.utils import formats
from django.utils.formats import get_format

import floppyforms as forms

from .utils.l10n import get_language_upper


class Datepicker(forms.TextInput):
    """
    Date field widget which use bootstrap-datepicker library.
    """

    @property
    def media(self):

        css = {
            'all': ('bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker3.min.css',)
        }
        js = ()

        if not settings.MYMONEY['USE_L10N_DIST'] and settings.MYMONEY['BOOTSTRAP_DATEPICKER_LANGCODE']:
            js += (
                'bower_components/bootstrap-datepicker/dist/locales/bootstrap-datepicker.{lang}.min.js'.format(
                    lang=settings.MYMONEY['BOOTSTRAP_DATEPICKER_LANGCODE'],
                ),
            )

        return forms.Media(css=css, js=js)

    def _format_value(self, value):
        return formats.localize_input(
            value,
            formats.get_format('DATE_INPUT_FORMATS')[0],
        )

    def build_attrs(self, extra_attrs=None, **kwargs):
        """
        Use this method instead of the classic __init__ in order to be
        executed at runtime due to locale switch.
        """
        date_input_format_js = get_format('DATE_INPUT_FORMAT_JS')
        if date_input_format_js == 'DATE_INPUT_FORMAT_JS':
            date_input_format_js = 'mm/dd/yyyy'

        attrs = {
            'size': 10,
            'data-provide': 'datepicker',
            'data-date-format': date_input_format_js,
            'data-date-language': get_language_upper(),
            'data-date-orientation': 'top auto',
            'data-date-autoclose': 1,
        }
        attrs.update(
            super(Datepicker, self).build_attrs(extra_attrs=extra_attrs, **kwargs)
        )
        return attrs
