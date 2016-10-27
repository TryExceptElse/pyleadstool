from leadmacro import Associations

from unittest import TestCase


class TestAssociations(TestCase):
    def setUp(self):
        test_file_path = ''
        self.assoc = Associations(test_file_path)
        self.assoc.add_assoc('test_key_a', 'test_value_a1')
        self.assoc.add_assoc('test_key_b', 'test_value_b1')
        self.assoc.add_assoc('test_key_c', 'test_value_c1')
        self.assoc.add_assoc('test_key_a', 'test_value_a2')

    def test_get_item_returns_correct_values(self):
        self.assertEqual('test_value_a1', self.assoc['test_key_a'][0])
        self.assertEqual('test_value_b1', self.assoc['test_key_b'][0])
        self.assertEqual('test_value_c1', self.assoc['test_key_c'][0])
        self.assertEqual('test_value_a2', self.assoc['test_key_a'][1])

    def test_assoc_can_be_cleaned(self):
        limit
