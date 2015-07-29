from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url


class AnonymousRedirectMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        if request.user.is_anonymous():
            path = request.get_full_path()
            resolved_login_url = resolve_url(settings.LOGIN_URL)

            if not path.startswith(resolved_login_url):
                return redirect_to_login(path, resolved_login_url)
