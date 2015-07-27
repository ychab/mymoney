import floppyforms.__future__ as forms

from .models import BankAccount


class BankAccountForm(forms.ModelForm):
    """
    Default bank account model form.
    """

    class Meta:
        model = BankAccount
        fields = ['label', 'balance', 'currency', 'owners']


class BankAccountFormWithoutOwners(BankAccountForm):
    """
     Bank account model form without owners field.
    """

    class Meta:
        model = BankAccount
        fields = ['label', 'balance', 'currency']
