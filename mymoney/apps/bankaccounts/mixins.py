from django.core.exceptions import PermissionDenied

from .forms import BankAccountForm, BankAccountFormWithoutOwners


class BankAccountAccessMixin(object):

    permissions = ()

    def dispatch(self, request, *args, **kwargs):
        """
        Allow access only if current user has permission and is owner of the
        bank account.
        """

        # No need to continue if permission is required and user hasn't it.
        if self.permissions and not request.user.has_perms(self.permissions):
            raise PermissionDenied

        # Only owner have access.
        if not self.get_object().owners.filter(pk=request.user.pk).exists():
            raise PermissionDenied

        return super(BankAccountAccessMixin, self).dispatch(
            request, *args, **kwargs)


class BankAccountSaveFormMixin(object):

    def get_form_class(self):
        """
        Return appropriate bank account model form to use depending on current
        user permissions.
        """
        if self.request.user.has_perm('bankaccounts.administer_owners'):
            return BankAccountForm
        return BankAccountFormWithoutOwners
