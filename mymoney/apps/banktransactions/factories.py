import datetime

import factory
from factory import fuzzy
from dateutil.relativedelta import relativedelta

from mymoney.apps.bankaccounts.factories import BankAccountFactory

from .models import BankTransaction


class AbstractBankTransactionFactory(factory.DjangoModelFactory):

    class Meta:
        abstract = True

    label = factory.Sequence(lambda n: 'test_%d' % n)
    bankaccount = factory.SubFactory(BankAccountFactory)
    date = fuzzy.FuzzyDate(datetime.date.today() - relativedelta(months=1))
    amount = fuzzy.FuzzyDecimal(-1000)
    currency = factory.SelfAttribute('bankaccount.currency')
    payment_method = fuzzy.FuzzyChoice(dict(BankTransaction.PAYMENT_METHODS).keys())


class BankTransactionFactory(AbstractBankTransactionFactory):

    class Meta:
        model = BankTransaction
