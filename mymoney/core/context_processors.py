from django.conf import settings

from mymoney.apps.bankaccounts.models import BankAccount
from mymoney.core.utils.l10n import get_language_upper


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

    if settings.MYMONEY['USE_L10N_DIST']:
        data['dist_js_src'] = "dist/js/mymoney.min.{lang}.js".format(lang=get_language_upper())
    else:
        data['dist_js_src'] = 'dist/js/mymoney.min.js'

    return data
