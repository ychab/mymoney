from django.utils.functional import cached_property

from mymoney.apps.banktransactions.models import BankTransaction

from .forms import RatioForm


class SessionViewMixin(object):
    """
    Mixin to store session data for a given key.
    """

    _session_key = None

    @property
    def session_data(self):
        return self.request.session.get(self._session_key, {})

    @session_data.setter
    def session_data(self, value):
        self.request.session[self._session_key] = value

    @session_data.deleter
    def session_data(self):
        if self._session_key in self.request.session:
            del self.request.session[self._session_key]


class RatioViewMixin(SessionViewMixin):
    """
    Mixin ratio view to use same session data and base queryset.
    """

    _session_key = 'banktransactionanalyticratioform'

    @property
    def base_queryset(self):

        qs = BankTransaction.objects.filter(
            bankaccount=self.bankaccount,
            status=BankTransaction.STATUS_ACTIVE,
        )

        filters = self.session_data.get('filters', {})
        qs = qs.filter(
            date__range=(filters['date_start'], filters['date_end']),
        )

        if filters['type'] == RatioForm.SINGLE_DEBIT:
            qs = qs.filter(amount__lt=0)
        elif filters['type'] == RatioForm.SINGLE_CREDIT:
            qs = qs.filter(amount__gt=0)

        if 'reconciled' in filters:
            qs = qs.filter(reconciled=filters['reconciled'])

        return qs


class TrendTimeViewMixin(SessionViewMixin):
    """
    Mixin trendtime view to use same session data and base queryset.
    """

    _session_key = 'banktransactionanalytictrendtimeform'

    @cached_property
    def base_queryset(self):

        qs = BankTransaction.objects.filter(
            bankaccount=self.bankaccount,
            status=BankTransaction.STATUS_ACTIVE,
        )

        filters = self.session_data.get('filters', {})
        if 'reconciled' in filters:
            qs = qs.filter(reconciled=filters['reconciled'])

        return qs
