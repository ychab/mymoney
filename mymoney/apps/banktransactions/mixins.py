from django.core.exceptions import PermissionDenied

from mymoney.apps.bankaccounts.models import BankAccount

from .models import BankTransaction


class BankTransactionAccessMixin(object):
    """
    Mixin class to allow access if :
    - current user is superuser
    OR
    - owner of the bank account AND have permissions (if any)
    """

    bankaccount = None
    permissions = ()

    def dispatch(self, request, *args, **kwargs):

        # No need to continue if permission is required and user hasn't it.
        if not request.user.has_perms(self.permissions):
            raise PermissionDenied

        if 'bankaccount_pk' in kwargs:
            try:
                self.bankaccount = BankAccount.objects.get(
                    pk=kwargs['bankaccount_pk']
                )
            except BankAccount.DoesNotExist:
                raise PermissionDenied
        else:
            # Implicit get_object_or_404().
            self.bankaccount = self.get_object().bankaccount

        # Only owners of the related bank account have access.
        if not self.bankaccount.owners.filter(pk=request.user.pk).exists():
            raise PermissionDenied

        return super(BankTransactionAccessMixin, self).dispatch(
            request, *args, **kwargs)


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
