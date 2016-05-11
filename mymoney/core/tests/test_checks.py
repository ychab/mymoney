from django.core.checks import Critical, Warning, run_checks
from django.test import SimpleTestCase, override_settings


class AdminURLCheck(SimpleTestCase):

    @override_settings(MYMONEY={"ADMIN_BASE_URL": ''})
    def test_deploy_critical(self):
        errors = self.get_filtered_msgs(
            run_checks(include_deployment_checks=True)
        )
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors.pop(), Critical)

    @override_settings(MYMONEY={"ADMIN_BASE_URL": 'admin'})
    def test_deploy_warning(self):
        errors = self.get_filtered_msgs(
            run_checks(include_deployment_checks=True)
        )
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors.pop(), Warning)

    @override_settings(MYMONEY={"ADMIN_BASE_URL": 'foo'})
    def test_deploy_ok(self):
        errors = self.get_filtered_msgs(
            run_checks(include_deployment_checks=True)
        )
        self.assertFalse(errors)

    @override_settings(MYMONEY={"ADMIN_BASE_URL": ''})
    def test_no_deploy(self):
        errors = self.get_filtered_msgs(
            run_checks(include_deployment_checks=False)
        )
        self.assertFalse(errors)

    def get_filtered_msgs(self, msgs):
        return [msg for msg in msgs if msg.id == 'mymoney_admin_base_url']
