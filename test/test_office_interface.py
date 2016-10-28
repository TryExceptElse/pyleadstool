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
        row = leadmacro.Office.XW.Row(self.sheet, 2, 0)
        cells = [cell for cell in row]
        self.assertEqual(2, len(cells))
        self.assertIsInstance(cells[0], leadmacro.Cell)
        self.assertEqual('a3', cells[0].value)
        self.assertIsInstance(cells[1], leadmacro.Cell)
        self.assertEqual('b3', cells[1].value)


class TestCell(TestOfficeObj):
    def setUp(self):
        super().setUp()
        self.cell = leadmacro.Office.XW.Cell(self.sheet, (0, 2))
        self.cell2 = leadmacro.Office.XW.Cell(self.sheet, (3, 2))
        self.cell3 = leadmacro.Office.XW.Cell(self.sheet, (4, 2))
        self.cell4 = leadmacro.Office.XW.Cell(self.sheet, (5, 2))

    def test_cell_value_returns_str_value_correctly(self):
        self.assertEqual('a3', self.cell.value)

    def test_cell_string_returns_content_string_in_string_cell(self):
        self.assertEqual('a3', self.cell.string)

    def test_cell_float_returns_zero_when_cell_has_string_content(self):
        self.assertEqual(0, self.cell.float)

    def test_cell_value_returns_number_when_cell_contains_number(self):
        self.assertEqual(123456, self.cell2.value)

    def test_cell_string_returns_string_of_number_when_cell_contains_num(self):
        self.assertEqual('123456', self.cell2.string)

    def test_cell_float_returns_number_when_cell_contents_is_number(self):
        self.assertEqual(123456, self.cell2.float)

    def test_cell_value_returns_none_when_cell_content_is_empty(self):
        self.assertIsNone(self.cell3.value)

    def test_cell_string_is_zero_length_empty_string_when_cell_is_empty(self):
        self.assertEqual('', self.cell3.string)

    def test_cell_float_is_0_when_cell_content_is_empty(self):
        self.assertEqual(0, self.cell3.float)

    def test_value_returns_cell_value_with_whitespace(self):
        self.assertEqual('\nwhitespace    string', self.cell4.value)

    def test_value_without_whitespace_returns_value_when_no_whitespace(self):
        self.assertEqual('a3', self.cell.value_without_whitespace)

    def test_value_without_whitespace_returns_stripped_str(self):
        self.assertEqual(
            'whitespace string',
            self.cell4.value_without_whitespace
        )

    def test_has_whitespace_returns_correct_bool(self):
        self.assertFalse(self.cell.has_whitespace)

    def test_has_whitespace_returns_true_when_present(self):
        self.assertTrue(self.cell4.has_whitespace)

    def test_x_returns_correct_int(self):
        self.assertEqual(0, self.cell.x)

    def test_y_returns_correct(self):
        self.assertEqual(2, self.cell.y)

    def test_row_returns_row_including_cell(self):
        self.assertIsInstance(self.cell.row, leadmacro.Row)
        self.assertEqual(2, self.cell.row.index)

    def test_column_returns_column_including_cell(self):
        col = self.cell4.column
        self.assertIsInstance(col, leadmacro.Column)
        self.assertEqual(5, col.index)