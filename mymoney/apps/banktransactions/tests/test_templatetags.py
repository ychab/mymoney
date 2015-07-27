import unittest

from ..templatetags.banktransactions_tags import banktransactionfield


class TemplateTagsTestCase(unittest.TestCase):

    def test_banktransactionfield(self):

        form = {'banktransaction_1': True}
        self.assertTrue(banktransactionfield(form, 1))
        self.assertFalse(banktransactionfield(form, 2))
