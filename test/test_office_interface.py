from unittest import TestCase

try:
    import xlwings as xw
except NameError:
    xw = None

import os

import leadmacro
import settings


class TestOfficeObj(TestCase):
    test_resource_dir_name = 'test_resources'
    test_book_name = 'TestBook1.xlsx'

    app = None
    model = None
    book = None
    sheet = None

    @classmethod
    def setUpClass(cls):
        """
        Creates new app and xlwings interface
        :return:
        """
        if xw is None:
            raise OSError('Could not import xlwings, this likely means'
                          'that this test class is being run on a '
                          'non-Windows system.')
        cls.app = xw.App(visible=False)  # create app
        assert isinstance(cls.app, xw.App)
        # get test book
        path_to_book = os.path.join(
            settings.PROJECT_ROOT,
            cls.test_resource_dir_name,
            cls.test_book_name
        )
        cls.book = cls.app.books.open(path_to_book)

    @classmethod
    def tearDownClass(cls):
        """
        Shuts down app created for TestCellLine
        :return:
        """
        cls.app.kill()

    def setUp(self):
        self.model = leadmacro.Office.XW.Model(self.app)
        self.sheet = self.model['TestSheet1']
        assert isinstance(self.sheet, leadmacro.Sheet), self.sheet.__repr__()


class TestCellLine(TestOfficeObj):
    def testCellLineIteratesOverTestRow1Correctly(self):
        line_iterator = leadmacro.CellLine(self.sheet, 'x', 1).__iter__()
        first_cell = line_iterator.__next__()
        self.assertIsInstance(first_cell, leadmacro.Cell)
        self.assertEquals("2a", first_cell.value)
        line_iterator.__next__()
        string_cell = line_iterator.__next__()
        self.assertIsInstance(first_cell, leadmacro.Cell)
        self.assertIsNot(first_cell, string_cell)
        self.assertEqual('string', string_cell.value)

    def testCellLineIteratorTerminatesAfterAllCellsReturned(self):
        line_iterator = leadmacro.CellLine(self.sheet, 'x', 1).__iter__()
        line_iterator.__next__()
        line_iterator.__next__()
        line_iterator.__next__()
        line_iterator.__next__()
        line_iterator.__next__()
        try:
            self.assertRaises(StopIteration, line_iterator.__next__())
        except StopIteration:
            pass


class TestLineSeries(TestOfficeObj):
    def test_line_series_returns_each_column_in_turn(self):
        reference_line = leadmacro.Office.XW.Row(self.sheet, 3, 0)
        columns = [column for column in leadmacro.LineSeries(reference_line)]
        self.assertEqual(2, len(columns))
        self.assertIsInstance(columns[0], leadmacro.Column)
        self.assertEqual('headerA', columns[0].name)
        self.assertIsInstance(columns[1], leadmacro.Column)
        self.assertEqual('headerB', columns[1].name)

class TestRow(TestOfficeObj):
    def test_row_iterator_returns_each_cell_in_row(self):
        row = leadmacro.Office.XW.Row()