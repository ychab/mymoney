import datetime

from django.test import SimpleTestCase

from mymoney.core.widgets import Datepicker


class DatepickerWidgetTestCase(SimpleTestCase):

    def test_locale_media(self):

        with self.settings(USE_L10N_DIST=True):
            widget = Datepicker()
            self.assertFalse(widget.media._js)

        with self.settings(USE_L10N_DIST=False, BOOTSTRAP_DATEPICKER_LANGCODE=''):
            widget = Datepicker()
            self.assertFalse(widget.media._js)

        with self.settings(USE_L10N_DIST=False, BOOTSTRAP_DATEPICKER_LANGCODE='fr'):
            widget = Datepicker()
            self.assertIn(
                'bower_components/bootstrap-datepicker/dist/locales/bootstrap-datepicker.fr.min.js',
                widget.media._js
            )

        with self.settings(USE_L10N_DIST=False, BOOTSTRAP_DATEPICKER_LANGCODE='fr-CH'):
            widget = Datepicker()
            self.assertIn(
                'bower_components/bootstrap-datepicker/dist/locales/bootstrap-datepicker.fr-CH.min.js',
                widget.media._js
            )

    def test_attrs(self):

        with self.settings(LANGUAGE_CODE='it'):
            widget = Datepicker()
            attrs = widget.build_attrs()
            self.assertEqual(attrs['data-date-language'], 'it')

        with self.settings(LANGUAGE_CODE='fr-ch'):
            widget = Datepicker()
            attrs = widget.build_attrs()
            self.assertEqual(attrs['data-date-language'], 'fr-CH')

        widget = Datepicker()
        attrs = widget.build_attrs(extra_attrs={
            'placeholder': 'foo',
            'data-date-orientation': 'bottom right',
        })
        self.assertIn('placeholder', attrs)
        self.assertEqual(attrs['data-date-orientation'], 'bottom right')

    def test_format_value(self):

        with self.settings(LANGUAGE_CODE='en-us', DATE_INPUT_FORMATS=('%Y-%m-%d',)):
            widget = Datepicker()
            self.assertEqual(
                widget._format_value(datetime.date(2015, 6, 22)),
                '2015-06-22',
            )

        with self.settings(LANGUAGE_CODE='fr-fr', DATE_INPUT_FORMATS=('%d/%m/%Y',)):
            widget = Datepicker()
            self.assertEqual(
                widget._format_value(datetime.date(2015, 6, 22)),
                '22/06/2015',
            )
