from django.contrib.auth.mixins import UserPassesTestMixin

import floppyforms.__future__.models as model_forms


class BankAccountAccessMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        """
        Allow access only if current user is owner of the bank account.
        """
        return self.get_object().owners.filter(pk=self.request.user.pk).exists()


class BankAccountSaveFormMixin(object):

    def get_form_class(self):
        """
        Add dynamic field owner to defined fields and use floppyform.
        """
        fields = list(self.fields)
        if self.request.user.has_perm('bankaccounts.administer_owners'):
            fields.append('owners')

        return model_forms.modelform_factory(self.model, fields=fields)
