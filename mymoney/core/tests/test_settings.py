from django.conf import settings
from django.test import TestCase


class SettingsTestCase(TestCase):

    def test_admin_url(self):

        response = self.client.get(
            '/{path}'.format(path=settings.MYMONEY['ADMIN_BASE_URL']),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.wsgi_request.path,
            '/{path}/login/'.format(path=settings.MYMONEY['ADMIN_BASE_URL']),
        )
