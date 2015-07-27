from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

import floppyforms.__future__ as forms

from mymoney.apps.banktransactiontags.models import BankTransactionTag
from mymoney.core.widgets import Datepicker

from .models import BankTransaction


class BankTransactionListForm(forms.Form):

    label = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': ugettext_lazy('Label'),
        })
    )

    date_start = forms.DateField(
        required=False,
        widget=Datepicker(attrs={
            'placeholder': ugettext_lazy('Date start'),
        }),
    )
    date_end = forms.DateField(
        required=False,
        widget=Datepicker(attrs={
            'placeholder': ugettext_lazy('Date end'),
        }),
    )

    amount_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        localize=True,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': ugettext_lazy('Minimum amount'),
        }),
    )
    amount_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        localize=True,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': ugettext_lazy('Maximum amount'),
        }),
    )

    status = forms.ChoiceField(
        choices=(('', ugettext_lazy('Status?')),) + BankTransaction.STATUSES,
        initial='',
        required=False,
    )
    reconciled = forms.NullBooleanField(required=False)
    tags = forms.ModelMultipleChoiceField(
        queryset=BankTransactionTag.objects.none(),
        required=False
    )

    operation = forms.ChoiceField(
        choices=(),
        required=False,
    )

    def __init__(self, user, bt_ids, submit, *args, **kwargs):
        super(BankTransactionListForm, self).__init__(*args, **kwargs)

        self.fields['tags'].queryset = (
            BankTransactionTag.objects.get_user_tags_queryset(user)
        )
        self.fields['reconciled'].widget.choices[0] = ('1', _('Reconciled?'))

        for pk in bt_ids:
            self.fields['banktransaction_' + str(pk)] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'data-id': pk})
            )

        choices = ()
        if user.has_perm('banktransactions.change_banktransaction'):
            choices += (
                ('reconcile', _('Reconcile')),
                ('unreconcile', _('Unreconcile')),
            )
        if user.has_perm('banktransactions.delete_banktransaction'):
            choices += (
                ('delete', _('Delete')),
            )
        if choices:
            self.fields['operation'].choices = choices

        self._submit = submit

    def clean(self):
        cleaned_data = super(BankTransactionListForm, self).clean()

        if self._submit == 'filter':
            date_start = cleaned_data.get('date_start')
            date_end = cleaned_data.get('date_end')
            if date_start and date_end and date_start > date_end:
                raise forms.ValidationError(
                    _("Date start could not be greater than date end."),
                    code='date_start_greater',
                )

            amount_min = cleaned_data.get('amount_min', None)
            amount_max = cleaned_data.get('amount_max', None)
            if (amount_min is not None and amount_max is not None
                    and amount_min > amount_max):
                raise forms.ValidationError(
                    _("Minimum amount could not be greater than maximum "
                      "amount."),
                    code='amount_min_greater',
                )

        if self._submit == 'action' and cleaned_data['operation']:
            ids = set()
            for name, value in cleaned_data.items():
                if name.startswith('banktransaction_') and value:
                    ids.add(int(name[len('banktransaction_'):]))
            if not ids:
                raise forms.ValidationError(
                    _('To apply operations, you need to select some bank '
                      'transactions.'),
                    code='no_id',
                )
            cleaned_data['banktransactions'] = ids

        return cleaned_data


class BankTransactionUpdateForm(forms.ModelForm):

    class Meta:
        model = BankTransaction
        fields = ['label', 'date', 'amount', 'status', 'reconciled',
                  'payment_method', 'memo', 'tag']

    def __init__(self, user, *args, **kwargs):
        super(BankTransactionUpdateForm, self).__init__(*args, **kwargs)
        self.fields['tag'].queryset = (
            BankTransactionTag.objects.get_user_tags_queryset(user)
        )
        self.fields['date'].widget = Datepicker()


class BankTransactionCreateForm(BankTransactionUpdateForm):

    redirect = forms.BooleanField(label=_('Stay on page?'), required=False)
