from django.utils import timezone

from dateutil.relativedelta import relativedelta
from factory import fuzzy

from mymoney.apps.banktransactions.factories import \
    AbstractBankTransactionFactory

from .models import BankTransactionScheduler


class BankTransactionSchedulerFactory(AbstractBankTransactionFactory):

    class Meta:
        model = BankTransactionScheduler

    type = fuzzy.FuzzyChoice(dict(BankTransactionScheduler.TYPES).keys())
    recurrence = fuzzy.FuzzyInteger(0, 10)
    last_action = fuzzy.FuzzyDateTime(
        start_dt=timezone.now() - relativedelta(months=2),
    )
    state = fuzzy.FuzzyChoice(dict(BankTransactionScheduler.STATES).keys())
