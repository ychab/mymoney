from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import BankTransactionTagCreateForm, BankTransactionTagForm
from .mixins import BankTransactionTagAccessMixin
from .models import BankTransactionTag


class BankTransactionTagListView(generic.ListView):
    model = BankTransactionTag
    paginate_by = 50
    ordering = ['name']

    def get_queryset(self):
        return (
            BankTransactionTag.objects
            .get_user_tags_queryset(self.request.user)
            .select_related('owner')
        )


class BankTransactionTagCreateView(SuccessMessageMixin, generic.CreateView):
    model = BankTransactionTag
    form_class = BankTransactionTagCreateForm
    success_message = _(
        "Bank transaction tag %(name)s was created successfully."
    )

    def get_initial(self):
        initial = super(BankTransactionTagCreateView, self).get_initial()
        if self.request.GET.get('self-redirect', False):
            initial['redirect'] = True
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super(BankTransactionTagCreateView, self).form_valid(form)
        if form.cleaned_data['redirect']:

            url_redirect = reverse('banktransactiontags:create') + '?self-redirect=1'
            return HttpResponseRedirect(url_redirect)

        return response


class BankTransactionTagUpdateView(BankTransactionTagAccessMixin,
                                   SuccessMessageMixin, generic.UpdateView):
    model = BankTransactionTag
    form_class = BankTransactionTagForm
    success_message = _(
        "Bank transaction tag %(name)s was updated successfully."
    )
    permissions = ('banktransactiontags.change_banktransactiontag',)


class BankTransactionTagDeleteView(BankTransactionTagAccessMixin,
                                   generic.DeleteView):
    model = BankTransactionTag
    success_url = reverse_lazy('banktransactiontags:list')
    permissions = ('banktransactiontags.delete_banktransactiontag',)
