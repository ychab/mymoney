from importlib import reload

from django.test import TestCase, modify_settings, override_settings

import mymoney


@modify_settings(MIDDLEWARE_CLASSES={
    'remove': ['mymoney.core.middleware.AnonymousRedirectMiddleware'],
})
class AdminURLTestCase(TestCase):

    def test_change_admin_url(self):

        with override_settings(ROOT_URLCONF='mymoney.urls', ADMIN_BASE_URL='foo'):
            reload(mymoney.urls)
            response = self.client.get('/foo', follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.path, '/foo/login/')

            response = self.client.get('/admin', follow=True)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.wsgi_request.path, '/admin')

        # MUST be the last (to reset it to /admin).
        with override_settings(ROOT_URLCONF='mymoney.urls', ADMIN_BASE_URL='admin'):
            reload(mymoney.urls)
            response = self.client.get('/admin', follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.path, '/admin/login/')
