from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url
from django.urls import get_script_prefix
from django.utils.deprecation import MiddlewareMixin


class AnonymousRedirectMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):

        if request.user.is_anonymous():
            path = request.get_full_path()
            resolved_login_url = resolve_url(settings.LOGIN_URL)

            # /login, /login?next=foo or /admin must skip redirect.
            whitelist = (
                resolved_login_url,
                get_script_prefix() + settings.MYMONEY['ADMIN_BASE_URL'],
            )
            if path.startswith(whitelist):
                return

            return redirect_to_login(path, resolved_login_url)
