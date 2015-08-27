import datetime

from django.test import override_settings, SimpleTestCase

from mymoney.core.widgets import Datepicker


class DatepickerWidgetTestCase(SimpleTestCase):

    def test_locale_media(self):

        with override_settings(LANGUAGE_CODE='en-us'):
            widget = Datepicker()
            self.assertNotIn(
                'bower_components/bootstrap-datepicker/locales/bootstrap-datepicker.en.min.js',
                widget.media._js
            )

        with override_settings(LANGUAGE_CODE='fr-fr'):
            widget = Datepicker()
            self.assertIn(
                'bower_components/bootstrap-datepicker/locales/bootstrap-datepicker.fr.min.js',
                widget.media._js
            )

    def test_attrs(self):

        with override_settings(LANGUAGE_CODE='it'):
            widget = Datepicker()
            attrs = widget.build_attrs()
            self.assertEqual(attrs['data-date-language'], 'it')
            self.assertEqual(attrs['data-date-format'], 'mm/dd/yyyy')

        with override_settings(LANGUAGE_CODE='fr-fr', DATE_INPUT_FORMAT_JS='dd/mm/yyyy'):
            widget = Datepicker()
            attrs = widget.build_attrs()
            self.assertEqual(attrs['data-date-language'], 'fr')
            self.assertEqual(attrs['data-date-format'], 'dd/mm/yyyy')

        widget = Datepicker()
        attrs = widget.build_attrs(extra_attrs={
            'placeholder': 'foo',
            'data-date-orientation': 'bottom right',
        })
        self.assertIn('placeholder', attrs)
        self.assertEqual(attrs['data-date-orientation'], 'bottom right')

    def test_format_value(self):

        with override_settings(LANGUAGE_CODE='en-us', DATE_INPUT_FORMATS=('%Y-%m-%d',)):
            widget = Datepicker()
            self.assertEqual(
                widget._format_value(datetime.date(2015, 6, 22)),
                '2015-06-22',
            )

        with override_settings(LANGUAGE_CODE='fr-fr', DATE_INPUT_FORMATS=('%d/%m/%Y',)):
            widget = Datepicker()
            self.assertEqual(
                widget._format_value(datetime.date(2015, 6, 22)),
                '22/06/2015',
            )
