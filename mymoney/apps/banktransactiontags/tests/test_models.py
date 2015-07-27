import unittest

from mymoney.apps.bankaccounts.factories import BankAccountFactory
from mymoney.core.factories import UserFactory

from ..factories import BankTransactionTagFactory
from ..models import BankTransactionTag


class ManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.owner = UserFactory(username='owner')
        self.not_owner = UserFactory(username='not_owner')
        self.banktransactiontags = [
            BankTransactionTagFactory(owner=self.owner),
            BankTransactionTagFactory(owner=self.not_owner),
        ]

    def tearDown(self):
        UserFactory._meta.model.objects.all().delete()
        BankTransactionTagFactory._meta.model.objects.all().delete()

    def test_get_user_tags_without_bankaccount(self):

        tags = BankTransactionTag.objects.get_user_tags_queryset(self.owner)
        self.assertListEqual(
            [self.banktransactiontags[0].pk],
            sorted([tag.pk for tag in tags])
        )

    def test_get_user_tags_with_bankaccount(self):

        superowner = UserFactory(username='superowner', user_permissions='admin')
        banktransactiontag = BankTransactionTagFactory(owner=superowner)
        BankAccountFactory(owners=[self.owner, superowner])

        tags = BankTransactionTag.objects.get_user_tags_queryset(self.owner)
        self.assertListEqual(
            [
                self.banktransactiontags[0].pk,
                banktransactiontag.pk,
            ],
            sorted([tag.pk for tag in tags])
        )


class RelationshipTestCase(unittest.TestCase):

    def test_delete_owner(self):

        owner = UserFactory(username='owner')
        banktransactiontag = BankTransactionTagFactory(owner=owner)

        owner.delete()
        with self.assertRaises(BankTransactionTag.DoesNotExist):
            banktransactiontag.refresh_from_db()
