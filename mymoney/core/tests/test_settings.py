from importlib import reload

from django.conf import settings
from django.test import TestCase, modify_settings

import mymoney


@modify_settings(MIDDLEWARE_CLASSES={
    'remove': ['mymoney.core.middleware.AnonymousRedirectMiddleware'],
})
class AdminURLTestCase(TestCase):

    def test_change_admin_url(self):

        mymoney_settings = settings.MYMONEY.copy()
        mymoney_settings['ADMIN_BASE_URL'] = 'foo'
        with self.settings(ROOT_URLCONF='mymoney.urls', MYMONEY=mymoney_settings):
            reload(mymoney.urls)
            response = self.client.get('/foo', follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.path, '/foo/login/')

            response = self.client.get('/admin', follow=True)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.wsgi_request.path, '/admin')

        # MUST be the last (to reset it to /admin).
        mymoney_settings = settings.MYMONEY.copy()
        mymoney_settings['ADMIN_BASE_URL'] = 'admin'
        with self.settings(ROOT_URLCONF='mymoney.urls', MYMONEY=mymoney_settings):
            reload(mymoney.urls)
            response = self.client.get('/admin', follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.path, '/admin/login/')
