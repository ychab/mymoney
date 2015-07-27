from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .mixins import BankAccountAccessMixin, BankAccountSaveFormMixin
from .models import BankAccount


class BankAccountListView(generic.ListView):
    model = BankAccount

    def get_queryset(self):
        return BankAccount.objects.get_user_bankaccounts(self.request.user)


class BankAccountCreateView(BankAccountSaveFormMixin, SuccessMessageMixin,
                            generic.CreateView):
    model = BankAccount
    fields = ['label', 'balance', 'currency', 'owners']
    template_name_suffix = '_create_form'
    success_message = _("Bank account %(label)s was created successfully")

    def get_initial(self):
        initial = super(BankAccountCreateView, self).get_initial()
        initial['owners'] = (self.request.user,)
        return initial

    def form_valid(self, form):
        response = super(BankAccountCreateView, self).form_valid(form)
        if not self.request.user.has_perm('bankaccounts.administer_owners'):
            self.object.owners.add(self.request.user)
        return response


class BankAccountUpdateView(BankAccountAccessMixin, BankAccountSaveFormMixin,
                            SuccessMessageMixin, generic.UpdateView):
    model = BankAccount
    fields = ['label', 'balance', 'currency', 'owners']
    template_name_suffix = '_update_form'
    success_message = _("Bank account %(label)s was updated successfully")
    permissions = ('bankaccounts.change_bankaccount',)


class BankAccountDeleteView(BankAccountAccessMixin, generic.DeleteView):
    model = BankAccount
    success_url = reverse_lazy('bankaccounts:list')
    permissions = ('bankaccounts.delete_bankaccount',)
