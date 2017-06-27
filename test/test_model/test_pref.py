"""
Tests functionality of preferences module
"""

from unittest import TestCase

import tempfile

from leads.model.pref import Preferences


class TestPref(TestCase):

    def test_value_can_be_saved_to_file_and_retrieved(self):
        f_name = tempfile.NamedTemporaryFile().name

        pref1 = Preferences(f_name)
        pref1['k1'] = 'v1'
        pref1['k2'] = 'v2'
        pref1.save()

        pref2 = Preferences(f_name)
        pref2.load()
        self.assertEquals('v1', pref2['k1'])
        self.assertEquals('v2', pref2['k2'])
