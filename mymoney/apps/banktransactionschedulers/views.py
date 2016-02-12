from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from mymoney.apps.banktransactions.mixins import (
    BankTransactionAccessMixin, BankTransactionSaveViewMixin,
)
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.core.utils.dates import GRANULARITY_MONTH, GRANULARITY_WEEK

from .forms import (
    BankTransactionSchedulerCreateForm, BankTransactionSchedulerUpdateForm,
)
from .models import BankTransactionScheduler


class BankTransactionSchedulerListView(BankTransactionAccessMixin,
                                       generic.ListView):
    model = BankTransactionScheduler
    template_name = 'banktransactionschedulers/overview/index.html'
    paginate_by = 50

    def get_queryset(self):
        return (
            BankTransactionScheduler.objects
            .filter(bankaccount=self.bankaccount)
            .order_by('-last_action')
        )

    def get_context_data(self, **kwargs):
        context = super(BankTransactionSchedulerListView, self).get_context_data(**kwargs)
        context['bankaccount'] = self.bankaccount

        totals, summary = {}, {}
        manager = BankTransactionScheduler.objects

        total = 0
        totals['debit'] = manager.get_total_debit(self.bankaccount)
        totals['credit'] = manager.get_total_credit(self.bankaccount)

        for bts_type in BankTransactionScheduler.TYPES:
            key = bts_type[0]
            if key in totals['debit'] or key in totals['credit']:

                if key == BankTransactionScheduler.TYPE_WEEKLY:
                    granularity = GRANULARITY_WEEK
                else:
                    granularity = GRANULARITY_MONTH

                total_credit = totals['credit'].get(key, 0)
                total_debit = totals['debit'].get(key, 0)
                used = BankTransaction.objects.get_total_unscheduled_period(
                    self.bankaccount, granularity) or 0

                summary[key] = {
                    'type': bts_type[1],
                    'credit': total_credit,
                    'debit': total_debit,
                    'used': used,
                    'remaining': total_credit + total_debit + used,
                }
                summary[key]['total'] = total_credit + total_debit
                total += summary[key]['total']

        context['summary'] = summary
        context['total'] = total

        return context


class BankTransactionSchedulerCreateView(PermissionRequiredMixin,
                                         BankTransactionAccessMixin,
                                         BankTransactionSaveViewMixin,
                                         SuccessMessageMixin,
                                         generic.CreateView):
    model = BankTransactionScheduler
    form_class = BankTransactionSchedulerCreateForm
    permission_required = ('banktransactionschedulers.add_banktransactionscheduler',)
    success_message = _(
        "Bank transaction scheduler %(label)s was created successfully."
    )

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


class BankTransactionSchedulerUpdateView(PermissionRequiredMixin,
                                         BankTransactionAccessMixin,
                                         BankTransactionSaveViewMixin,
                                         SuccessMessageMixin,
                                         generic.UpdateView):
    model = BankTransactionScheduler
    form_class = BankTransactionSchedulerUpdateForm
    permission_required = ('banktransactionschedulers.change_banktransactionscheduler',)
    success_message = _(
        "Bank transaction scheduler %(label)s was updated successfully."
    )


class BankTransactionSchedulerDeleteView(PermissionRequiredMixin,
                                         BankTransactionAccessMixin,
                                         generic.DeleteView):
    model = BankTransactionScheduler
    permission_required = ('banktransactionschedulers.delete_banktransactionscheduler',)

    def get_success_url(self):

        self.success_url = reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.object.bankaccount.pk,
        })
        return super(BankTransactionSchedulerDeleteView, self).get_success_url()
