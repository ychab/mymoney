from django.core.exceptions import PermissionDenied


class BankTransactionTagAccessMixin(object):
    """
    Mixin to allow access on tag only for explicit owner or super user.
    """
    permissions = ()

    def dispatch(self, request, *args, **kwargs):

        # No need to continue if permission is denied.
        if not request.user.has_perms(self.permissions):
            raise PermissionDenied

        # Only strict owner with perm could edit or update it.
        if self.get_object().owner != request.user:
            raise PermissionDenied

        return super(BankTransactionTagAccessMixin, self).dispatch(
            request, *args, **kwargs
        )
