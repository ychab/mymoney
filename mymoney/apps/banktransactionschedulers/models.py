import logging
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from mymoney.apps.banktransactions.models import (
    AbstractBankTransaction, BankTransaction,
)
from mymoney.core.utils.dates import (
    GRANULARITY_MONTH, GRANULARITY_WEEK, get_datetime_ranges,
)

logger = logging.getLogger(__name__)


class BankTransactionSchedulerManager(models.Manager):

    def get_awaiting_banktransactions(self):
        """
        Return awaiting bank transaction scheduled. To be awaiting :
        - have explicit state BankTransactionScheduler.STATE_WAITING
        OR
        - have state BankTransactionScheduler.STATE_FINISHED and being lower
          than the recurring datetime, depending on its type.
        """
        month_start = get_datetime_ranges(timezone.now(), GRANULARITY_MONTH)[0]
        week_start = get_datetime_ranges(timezone.now(), GRANULARITY_WEEK)[0]

        monthly = (
            Q(type=BankTransactionScheduler.TYPE_MONTHLY)
            &
            Q(last_action__lt=month_start)
        )
        weekly = (
            Q(type=BankTransactionScheduler.TYPE_WEEKLY)
            &
            Q(last_action__lt=week_start)
        )

        return self.filter(
            (
                Q(state=BankTransactionScheduler.STATE_FINISHED)
                &
                (monthly | weekly)
            )
            |
            Q(state=BankTransactionScheduler.STATE_WAITING)
        )

    def get_total_debit(self, bankaccount):
        return dict(
            self.filter(
                bankaccount=bankaccount,
                amount__lt=0,
            )
            .exclude(status=BankTransactionScheduler.STATUS_INACTIVE)
            .values_list('type')
            .annotate(total=Sum('amount'))
        )

    def get_total_credit(self, bankaccount):
        return dict(
            self.filter(
                bankaccount=bankaccount,
                amount__gt=0,
            )
            .exclude(status=BankTransactionScheduler.STATUS_INACTIVE)
            .values_list('type')
            .annotate(total=Sum('amount'))
        )


class BankTransactionScheduler(AbstractBankTransaction):
    """
    Concrete bank transaction model class to be cloned periodically.
    """

    TYPE_MONTHLY = 'monthly'
    TYPE_WEEKLY = 'weekly'
    TYPES = (
        (TYPE_MONTHLY, _('Monthly')),
        (TYPE_WEEKLY, _('Weekly')),
    )

    STATE_WAITING = 'waiting'
    STATE_FINISHED = 'finished'
    STATE_FAILED = 'failed'
    STATES = (
        (STATE_WAITING, _('Waiting')),
        (STATE_FINISHED, _('Finished')),
        (STATE_FAILED, _('Failed')),
    )

    type = models.CharField(
        choices=TYPES,
        max_length=32,
        default=TYPE_MONTHLY,
        verbose_name=_('Type'),
        help_text=_('The type of recurrence to be applied.'),
    )
    recurrence = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Recurrence'),
        help_text=_('How many time the bank transaction should be cloned.')
    )
    last_action = models.DateTimeField(
        null=True,
        editable=False,
        help_text=_('Last time the scheduled bank transaction has been '
                    'cloned.')
    )
    state = models.CharField(
        choices=STATES,
        max_length=32,
        default=STATE_WAITING,
        editable=False,
        help_text=_('State of the scheduled bank transaction.'),
    )

    objects = BankTransactionSchedulerManager()

    class Meta:
        db_table = 'banktransactionschedulers'
        index_together = [
            "state",
            "last_action",
        ]

    def get_absolute_url(self):
        return reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': self.bankaccount.pk
        })

    def clone(self):
        """
        Clone the model instance into a BankTransaction instance.
        """

        try:
            with transaction.atomic():

                # Create a new bank transaction based on model.
                if self.type == BankTransactionScheduler.TYPE_MONTHLY:
                    datedelta = relativedelta(months=1)
                elif self.type == BankTransactionScheduler.TYPE_WEEKLY:  # pragma: no branch
                    datedelta = timedelta(weeks=1)

                BankTransaction.objects.create(
                    label=self.label,
                    bankaccount=self.bankaccount,
                    date=self.date + datedelta,
                    amount=self.amount,
                    currency=self.currency,
                    status=self.status,
                    reconciled=False,
                    payment_method=self.payment_method,
                    memo=self.memo,
                    tag=self.tag,
                    scheduled=True,
                )

                # Then update the scheduled bank transaction or delete it.
                if self.recurrence is not None:
                    self.recurrence -= 1

                if self.recurrence is not None and self.recurrence <= 0:
                    self.delete()
                else:
                    self.date = self.date + datedelta
                    self.last_action = timezone.now()
                    self.state = BankTransactionScheduler.STATE_FINISHED
                    self.save()

        except Exception as e:

            logger.exception(
                _('Error occured while trying to clone scheduled bank '
                  'transaction %(id)d with exception : %(msg)s') % {
                    'id': self.pk,
                    'msg': e
                }
            )

            try:
                # Try to release lock with an explicit failed state. Use
                # low-level API to prevent potential new exception (instead of
                # a new save() method with update_fields).
                BankTransactionScheduler.objects.filter(pk=self.pk).update(
                    state=BankTransactionScheduler.STATE_FAILED
                )
            except Exception:
                pass
