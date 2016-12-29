import os

import settings

from unittest import TestCase

from leadmacro import RowLog


class TestRowLog(TestCase):
    test_resource_dir_name = 'test_resources'
    test_log_dir_name = 'test_log_dir'

    def setUp(self):
        self.row_log_dir = os.path.join(
            settings.PROJECT_ROOT,
            self.test_resource_dir_name,
            self.test_log_dir_name
        )
        self.row_log = RowLog(self.row_log_dir)

    def test_row_log_finds_all_groups(self):
        self.assertIn('test_group_1', self.row_log.group_names)
        self.assertIn('test_group_2', self.row_log.group_names)

    def test_add_group_adds_a_directory(self):
        new_group_name = 'a_new_group'
        self.row_log.new_group(new_group_name)
        self.assertIn(
            new_group_name,
            [os.path.basename(path) for path in os.listdir(self.row_log_dir)]
        )
        # delete created folder
        os.removedirs(os.path.join(self.row_log_dir, new_group_name))
