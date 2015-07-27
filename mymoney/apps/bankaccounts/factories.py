import factory
from factory import fuzzy

from .models import BankAccount


class BankAccountFactory(factory.DjangoModelFactory):

    class Meta:
        model = BankAccount

    label = factory.Sequence(lambda n: 'test_%d' % n)
    balance = fuzzy.FuzzyDecimal(-10000, 10000, precision=2)
    currency = fuzzy.FuzzyChoice(['EUR', 'USD'])

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):

        if create and extracted:
            self.owners = extracted
