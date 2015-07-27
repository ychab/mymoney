from mymoney.apps.bankaccounts.models import BankAccount


def extra(request):
    """
    Context processor to inject (and cache queryset) the bank accounts of the
    current user.
    """
    data = {}

    if request.user.is_authenticated():
        data['user_bankaccounts'] = BankAccount.objects.get_user_bankaccounts(
            request.user
        )

    return data
