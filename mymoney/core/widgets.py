from django.utils import formats
from django.utils.formats import get_format
from django.utils.translation import get_language

import floppyforms as forms


class Datepicker(forms.TextInput):
    """
    Date field widget which use bootstrap-datepicker library.
    """

    @property
    def media(self):

        css = {
            'all': ('bootstrap-datepicker/css/bootstrap-datepicker3.min.css',)
        }
        js = ('bootstrap-datepicker/js/bootstrap-datepicker.min.js',)

        lang = get_language()[:2]
        if lang != 'en':
            js += (
                'bootstrap-datepicker/locales/bootstrap-datepicker.{lang}.min.js'.format(
                    lang=lang,
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
        try:
            date_input_format_js = get_format('DATE_INPUT_FORMAT_JS')
        except AttributeError:
            date_input_format_js = 'mm/dd/yyyy'

        attrs = {
            'size': 10,
            'data-provide': 'datepicker',
            'data-date-format': date_input_format_js,
            'data-date-language': get_language()[:2],
            'data-date-orientation': 'top auto',
            'data-date-autoclose': 1,
        }
        attrs.update(
            super(Datepicker, self).build_attrs(extra_attrs=extra_attrs, **kwargs)
        )
        return attrs
