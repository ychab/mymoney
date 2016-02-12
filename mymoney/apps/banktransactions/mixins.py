from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from mymoney.apps.bankaccounts.models import BankAccount

from .models import BankTransaction


class BankTransactionAccessMixin(UserPassesTestMixin):
    """
    Allow access if current user is owner of the bank account
    """
    raise_exception = True

    bankaccount = None

    def test_func(self):

        if 'bankaccount_pk' in self.kwargs:
            self.bankaccount = get_object_or_404(BankAccount, pk=self.kwargs['bankaccount_pk'])
        else:
            # Implicit get_object_or_404().
            self.bankaccount = self.get_object().bankaccount

        return self.bankaccount.owners.filter(pk=self.request.user.pk).exists()


class BankTransactionSaveViewMixin(object):
    """
    Model edit view mixin to :
    - inject current user object
    - force bankaccount relationship with bank transaction
    """
    model = BankTransaction

    def get_form_kwargs(self):
        kwargs = super(BankTransactionSaveViewMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.bankaccount = self.bankaccount
        return super(BankTransactionSaveViewMixin, self).form_valid(form)
