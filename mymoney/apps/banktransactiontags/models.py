from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mymoney.apps.bankaccounts.models import BankAccount


class BankTransactionTagManager(models.Manager):

    def get_user_tags_queryset(self, user):

        user_model = get_user_model()

        # Not a real subquery, 2 queries are finally executed!
        return (
            self
            .filter(
                models.Q(owner=user.pk) |
                models.Q(
                    owner__in=user_model.objects.raw(
                        raw_query="""
                            SELECT u.id
                            FROM {table_user} AS u
                            JOIN {table_owners} AS ba
                                ON u.id = ba.user_id
                            JOIN {table_owners} AS ba_rel
                                ON ba.bankaccount_id = ba_rel.bankaccount_id
                            WHERE u.id != %s AND ba_rel.user_id = %s
                            GROUP BY u.id
                            """.format(table_user=user_model._meta.db_table,
                                       table_owners=BankAccount.owners.field.db_table),
                        params=[user.pk, user.pk],
                    )
                )
            )
            .order_by('name')
        )


class BankTransactionTag(models.Model):

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tags',
    )

    objects = BankTransactionTagManager()

    class Meta:
        db_table = 'banktransactiontags'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('banktransactiontags:list')
