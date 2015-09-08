from django.conf import settings
from django.core.checks import Critical, Tags, Warning, register


@register(Tags.security, deploy=True)
def admin_url_prefix_check(app_configs, **kwargs):
    errors = []

    if not settings.MYMONEY['ADMIN_BASE_URL']:

        errors.append(
            Critical("(MyMoney) ADMIN_BASE_URL must be set in your config.",
                     id='mymoney_admin_base_url')
        )
    elif settings.MYMONEY['ADMIN_BASE_URL'] == 'admin':

        errors.append(
            Warning("(MyMoney) ADMIN_BASE_URL setting is default to common "
                    "'admin' value. You are encourage to change it.",
                    id='mymoney_admin_base_url')
        )

    return errors
