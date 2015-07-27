from django.utils.translation import ugettext as _

import floppyforms.__future__ as forms

from mymoney.apps.banktransactions.forms import BankTransactionUpdateForm
from mymoney.core.widgets import Datepicker

from .models import BankTransactionScheduler


class BankTransactionSchedulerUpdateForm(BankTransactionUpdateForm):

    class Meta:
        model = BankTransactionScheduler
        fields = ['label', 'date', 'amount', 'status',
                  'payment_method', 'memo', 'tag', 'type', 'recurrence']

    def __init__(self, *args, **kwargs):
        super(BankTransactionSchedulerUpdateForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = Datepicker()


class BankTransactionSchedulerCreateForm(BankTransactionSchedulerUpdateForm):

    start_now = forms.BooleanField(label=_('Start it now?'), required=False)
