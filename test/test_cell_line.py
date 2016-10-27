from unittest import TestCase

import leadmacro


class TestCellLine(TestCase):
    def setUp(self):
        self.model = leadmacro.Office.get_model()
        self.sheet = self.model['TestSheet1']