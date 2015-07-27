import datetime

from django.utils import formats
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

import floppyforms as forms

from mymoney.apps.banktransactiontags.models import BankTransactionTag
from mymoney.core.widgets import Datepicker
from mymoney.core.utils.dates import GRANULARITY_MONTH, GRANULARITY_WEEK


class RatioForm(forms.Form):
    """
    Form to display bank transaction sums grouped by tags.
    """

    CREDIT = 'credit'
    DEBIT = 'debit'
    TYPES = (
        (CREDIT, ugettext_lazy('Income')),
        (DEBIT, ugettext_lazy('Expenses')),
    )
    type = forms.ChoiceField(choices=TYPES, initial=DEBIT)

    CHART_DOUGHNUT = 'doughtnut'
    CHART_PIE = 'pie'
    CHART_POLAR = 'polar'
    CHART_TYPES = (
        (CHART_DOUGHNUT, ugettext_lazy('Doughnut')),
        (CHART_PIE, ugettext_lazy('Pie')),
        (CHART_POLAR, ugettext_lazy('Polar area')),
    )
    chart = forms.ChoiceField(
        choices=CHART_TYPES,
        initial=CHART_DOUGHNUT,
        required=False,
    )

    date_start = forms.DateField(
        widget=Datepicker(attrs={
            'placeholder': ugettext_lazy('Date start'),
        }),
    )
    date_end = forms.DateField(
        widget=Datepicker(attrs={
            'placeholder': ugettext_lazy('Date end'),
        }),
    )

    reconciled = forms.NullBooleanField(required=False)

    tags = forms.ModelMultipleChoiceField(
        queryset=BankTransactionTag.objects.none(),
        required=False
    )

    sum_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        localize=True,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Minimum sum'),
        }),
    )
    sum_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        localize=True,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Maximum sum'),
        }),
    )

    def __init__(self, user, *args, **kwargs):
        super(RatioForm, self).__init__(*args, **kwargs)

        self.fields['tags'].queryset = (
            BankTransactionTag.objects.get_user_tags_queryset(user)
        )
        self.fields['reconciled'].widget.choices[0] = ('1', _('Reconciled?'))

    def clean(self):
        cleaned_data = super(RatioForm, self).clean()

        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')
        if date_start and date_end and date_start > date_end:
            raise forms.ValidationError(
                _("Date start could not be greater than date end."),
                code='date_start_greater',
            )

        sum_min = cleaned_data.get('sum_min', None)
        sum_max = cleaned_data.get('sum_max', None)
        if sum_min is not None and sum_max is not None and sum_min > sum_max:
            raise forms.ValidationError(
                _("Minimum sum could not be greater than maximum sum."),
                code='sum_min_greater',
            )

        return cleaned_data


class TrendtimeForm(forms.Form):
    """
    Form to display bank transaction sums with a timeline.
    """
    CHART_LINE = 'line'
    CHART_BAR = 'bar'
    CHART_RADAR = 'radar'
    CHART_TYPES = (
        (CHART_LINE, ugettext_lazy('Line')),
        (CHART_BAR, ugettext_lazy('Bar')),
        (CHART_RADAR, ugettext_lazy('Radar')),
    )
    chart = forms.ChoiceField(choices=CHART_TYPES, initial=CHART_LINE)

    GRANULARITY_CHOICES = (
        (GRANULARITY_WEEK, ugettext_lazy('Week')),
        (GRANULARITY_MONTH, ugettext_lazy('Month')),
    )
    granularity = forms.ChoiceField(
        choices=GRANULARITY_CHOICES,
        initial=GRANULARITY_MONTH,
    )

    date = forms.DateField(required=True, widget=Datepicker())

    reconciled = forms.NullBooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(TrendtimeForm, self).__init__(*args, **kwargs)
        self.fields['reconciled'].widget.choices[0] = ('1', _('Reconciled?'))
        self.fields['date'].initial = formats.date_format(
            datetime.date.today(),
            'SHORT_DATE_FORMAT',
        )
