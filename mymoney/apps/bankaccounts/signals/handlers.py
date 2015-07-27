from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from ..models import BankAccount


@receiver(post_delete, sender=get_user_model())
def delete_orphans(sender, **kwargs):
    """
    When an user instance is deleted, delete his bank accounts if no more
    owners exist for these bank accounts.
    """
    BankAccount.objects.delete_orphans()
