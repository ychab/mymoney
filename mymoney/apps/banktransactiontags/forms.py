from django.utils.translation import ugettext as _

import floppyforms.__future__ as forms

from .models import BankTransactionTag


class BankTransactionTagForm(forms.ModelForm):

    class Meta:
        model = BankTransactionTag
        fields = ['name']


class BankTransactionTagCreateForm(BankTransactionTagForm):

    redirect = forms.BooleanField(label=_('Stay on page?'), required=False)
