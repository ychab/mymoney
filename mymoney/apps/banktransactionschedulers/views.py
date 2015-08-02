from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from mymoney.apps.banktransactions.mixins import (
    BankTransactionAccessMixin, BankTransactionSaveViewMixin
)

from .forms import (
    BankTransactionSchedulerCreateForm, BankTransactionSchedulerUpdateForm
)
from .models import BankTransactionScheduler


class BankTransactionSchedulerListView(BankTransactionAccessMixin,
                                       generic.ListView):
    model = BankTransactionScheduler
    paginate_by = 50

    def get_queryset(self):
        return (
            BankTransactionScheduler.objects
            .filter(bankaccount=self.bankaccount)
            .order_by('-last_action')
        )

    def get_context_data(self, **kwargs):
        context = super(BankTransactionSchedulerListView, self).get_context_data(**kwargs)

        total_debit = (
            BankTransactionScheduler.objects.get_total_debit(self.bankaccount)
        )
        total_credit = (
            BankTransactionScheduler.objects.get_total_credit(self.bankaccount)
        )

        summary = {}
        total = 0
        for bts_type in BankTransactionScheduler.TYPES:
            key = bts_type[0]
            summary[key] = {
                'type': bts_type[1],
                'credit': total_credit[key] if key in total_credit else 0,
                'debit': total_debit[key] if key in total_debit else 0,
            }
            summary[key]['total'] = summary[key]['credit'] + summary[key]['debit']
            total += summary[key]['total']

        context['summary'] = summary
        context['total'] = total
        context['currency'] = self.bankaccount.currency
        return context


class BankTransactionSchedulerCreateView(BankTransactionAccessMixin,
                                         BankTransactionSaveViewMixin,
                                         SuccessMessageMixin,
                                         generic.CreateView):
    model = BankTransactionScheduler
    form_class = BankTransactionSchedulerCreateForm
    success_message = _(
        "Bank transaction scheduler %(label)s was created successfully."
    )
    permissions = ('banktransactionschedulers.add_banktransactionscheduler',)

    def get_initial(self):

        initial = super(BankTransactionSchedulerCreateView, self).get_initial()
        if self.request.GET.get('self-redirect', False):
            initial['redirect'] = True
        return initial

    def form_valid(self, form):
        response = (
            super(BankTransactionSchedulerCreateView, self).form_valid(form)
        )

        if form.cleaned_data['start_now']:
            self.object.clone()

        if form.cleaned_data['redirect']:
            url_redirect = reverse('banktransactionschedulers:create', kwargs={
                'bankaccount_pk': self.object.bankaccount.pk,
            }) + '?self-redirect=1'
            return HttpResponseRedirect(url_redirect)

        return response


class BankTransactionSchedulerUpdateView(BankTransactionAccessMixin,
                                         BankTransactionSaveViewMixin,
                                         SuccessMessageMixin,
                                         generic.UpdateView):
    model = BankTransactionScheduler
    form_class = BankTransactionSchedulerUpdateForm
    success_message = _(
        "Bank transaction scheduler %(label)s was updated successfully."
    )
    permissions = ('banktransactionschedulers.change_banktransactionscheduler',)


class BankTransactionSchedulerDeleteView(BankTransactionAccessMixin,
                                         generic.DeleteView):
    model = BankTransactionScheduler
    permissions = ('banktransactionschedulers.delete_banktransactionscheduler',)

    def get_success_url(self):

        self.success_url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.object.bankaccount.pk,
        })
        return super(BankTransactionSchedulerDeleteView, self).get_success_url()
