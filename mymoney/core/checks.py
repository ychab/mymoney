from django.conf import settings
from django.core.checks import Critical, register, Tags, Warning


@register(Tags.security, deploy=True)
def admin_url_prefix_check(app_configs, **kwargs):
    errors = []

    if (not hasattr(settings, 'ADMIN_BASE_URL') or
            not settings.ADMIN_BASE_URL):

        errors.append(
            Critical("(MyMoney) ADMIN_BASE_URL doesn't exists and must be set "
                     "in your config.", id='mymoney_admin_base_url')
        )
    elif settings.ADMIN_BASE_URL == 'admin':

        errors.append(
            Warning("(MyMoney) ADMIN_BASE_URL setting is default to common "
                    "'admin' value. You are encourage to change it.",
                    id='mymoney_admin_base_url')
        )

    return errors
