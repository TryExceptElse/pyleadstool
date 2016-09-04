"""
    Copyright (c) 2016 John Schwarz


    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy,
    modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.



PRE-DELIVERABLE STATE


As a macro, all LOC are going to be located within this module.
It may not be the best organization, but it allows easier mobility of
the produced macro.

This is intended to be run as a LibreOffice Calc macro

Contents:

PyUno handling
Translations
GUI

KNOWN BUGS:

Attempting to open two instances of the macro simultaneously will
freeze both macros and the office program

INSTALL:
for libreoffice, requires python scripts module installed.
in ubuntu, this can be installed via
    'apt-get install libreoffice-script-provider-python'

"""


import PyQt5.QtWidgets as QtW
import sys

DESKTOP = XSCRIPTCONTEXT.getDesktop()  # not an error; provided by macro caller
MODEL = DESKTOP.getCurrentComponent()

MAX_CELL_GAP = 10  # max distance between inhabited cells in the workbook

APP_WINDOW_TITLE = 'Lead Macro'
DEFAULT_WIDGET_X = 512
DEFAULT_WIDGET_Y = 512
DEFAULT_WIDGET_H = 512
DEFAULT_WIDGET_W = 1024
DEFAULT_CONTENT_MARGIN_X = 15
DEFAULT_CONTENT_MARGIN_Y = 5

STANDARD_GRID_SPACING = 10

NONE_STRING = '< None >'

# colors #

DEFAULT_COLOR = -1
WHITE = 0xffffff
FIREBRICK = 0xB22222
CORAL = 0xFF7F50
ORANGE = 0xBDB76B
KHAKI = 0xF0E68C

###############################################################################
# Model Classes / PyUno class handling


class Model:
    """
    Handles usages of PyUno Model
    """
    def __init__(self, py_uno_model):
        if not hasattr(py_uno_model, 'Sheets'):
            raise AttributeError(
                'Model does not have Sheets. '
                'This macro needs to be run from a calc workbook.'
            )
        self.model = py_uno_model

    def __getitem__(self, item):
        assert isinstance(item, (str, int))
        if isinstance(item, int):
            return Sheet(self.model.Sheets.getByIndex(item))
        else:
            return Sheet(self.model.Sheets.getByName(item))

    def sheet_exists(self, *args):
        """
        Checks each string passed as arg to see if it exists as a
        sheet name. If so, returns it, otherwise, moves to the next
        :param args: strings
        :return: str of first viable sheet name or None if no
        viable name is found
        """
        assert all([isinstance(arg, str) for arg in args])
        for sheet_name in args:
            try:
                self.model.Sheets.getByName(sheet_name)
            except:  # todo: find actual exception class
                pass
            else:
                return sheet_name


class Sheet:
    """
    Handles usage of a workbook sheet
    """
    sheet = None
    _reference_row_index = 0
    _reference_column_index = 0

    def __init__(self, sheet, reference_row_index=0, reference_column_index=0):
        self.sheet = sheet
        self.reference_row_index = reference_row_index
        self.reference_column_index = reference_column_index

    def get_column(self, column_identifier):
        """
        Gets column from name
        :param column_identifier: str or int
        identifying the column to retrieve
        :return: Column
        """
        assert isinstance(column_identifier, (int, str)), \
            'getitem must be passed an int or str, got %s' % column_identifier
        if isinstance(column_identifier, int):
            column_index = column_identifier
        else:
            for i, cell in enumerate(self.reference_row):
                if cell.value == column_identifier:
                    column_index = i
                    break
            else:
                return
        return Column(sheet=self.sheet,
                      column_index=column_index,
                      reference_column_index=self.reference_column_index)

    def get_row(self, row_identifier):
        """
        Gets row from identifier
        :param row_identifier:
        :return:
        """
        assert isinstance(row_identifier, (int, str)), \
            'getitem must be passed an int or str, got %s' % row_identifier
        row_index = None
        if isinstance(row_identifier, int):
            row_index = row_identifier
        else:
            for i, cell in enumerate(self.reference_column):
                if cell.value == row_identifier:
                    row_index = i
                    break
        return Row(sheet=self.sheet,
                   row_index=row_index,
                   reference_row_index=self.reference_row_index
                   ) if row_index is not None else None

    def get_cell(self, position):
        try:
            position = tuple(position)
        except ValueError:
            raise ValueError('position passed to \'get cell\' method '
                             'must be a tuple or convertible to a tuple')
        return Cell(self.sheet, position)

    @property
    def columns(self):
        """
        Returns list of columns in sheet
        :return: list of Columns
        """
        return [self.get_column(x) for x in range(len(self.get_row(0)))]

    @property
    def rows(self):
        """
        Returns list of rows in sheet
        :return: list of Rows
        """
        return [self.get_row(y) for y in range(len(self.get_column(0)))]

    @property
    def reference_row_index(self):
        """
        Gets reference row index
        :return: int
        """
        return self._reference_row_index

    @reference_row_index.setter
    def reference_row_index(self, new_index):
        """
        Sets reference row index
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._reference_row_index = new_index

    @property
    def reference_column_index(self):
        """
        Gets reference column index
        :return: int
        """
        return self._reference_column_index

    @reference_column_index.setter
    def reference_column_index(self, new_index):
        """
        Sets reference column index
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._reference_column_index = new_index

    @property
    def reference_row(self):
        """
        Gets reference row
        :return: Row
        """
        return Row(sheet=self.sheet,
                   row_index=self.reference_row_index)

    @property
    def reference_column(self):
        """
        Gets reference column
        :return: Column
        """
        return Column(sheet=self.sheet,
                      column_index=self.reference_column_index)


class Column:
    """
    Handles usage of a column within a sheet
    """
    def __init__(self, sheet, column_index, reference_column_index=0):
        self.sheet = sheet
        self.column_index = column_index
        self.reference_column_index = reference_column_index
        self._length = None

    def __getitem__(self, cell_identifier):
        """
        Gets cell from passed identifier
        :param cell_identifier: str or int
        :return: Cell
        """
        assert isinstance(cell_identifier, (int, str))
        if isinstance(cell_identifier, int):
            return Cell(self.sheet, (self.column_index, cell_identifier))
        else:
            for x, cell in enumerate(self.reference_column):
                if cell.value == cell_identifier:
                    return self[x]

    def __iter__(self):
        """
        Returns iterable line of cells
        :return: Iterable
        """
        return CellLine(sheet=self.sheet,
                        axis='y',
                        index=self.column_index)

    def __len__(self):
        n = 0
        for each in self:
            n += 1
        return n

    @property
    def reference_column(self):
        """
        Gets reference column
        :return: Column
        """
        return Column(sheet=self.sheet,
                      column_index=self.reference_column_index)

    def find_duplicates(self):
        """
        returns a list of indexes at which duplications occur.
        The first instance of a cell value will not be considered a
        duplicate.
        :return: list of int
        """
        cell_values = set()
        duplicate_indexes = []
        for i, cell in enumerate(self):
            if cell.value in cell_values:
                duplicate_indexes.append(i)
            cell_values.add(cell.value)
        return duplicate_indexes

    @property
    def name(self):
        """
        Returns name of column, based on value stored in header
        :return: str
        """
        return self[0].value


class Row:
    """
    Handles usage of a row within a sheet
    """
    def __init__(self, sheet, row_index, reference_row_index=0):
        self.sheet = sheet
        self.row_index = row_index
        self.reference_row_index = reference_row_index

    def __getitem__(self, item):
        assert isinstance(item, (str, int))
        if isinstance(item, int):
            return Cell(sheet=self.sheet, position=(item, self.row_index))
        else:
            for x, cell in enumerate(self.reference_row):
                if cell.value == item:
                    return self[x]

    def __iter__(self):
        return CellLine(sheet=self.sheet,
                        axis='x',
                        index=self.row_index)

    def __len__(self):
        n = 0
        for each in self:
            n += 1
        return n

    @property
    def reference_row(self):
        """
        Gets reference row
        :return: Row
        """
        return Row(sheet=self.sheet,
                   row_index=self.reference_row_index)


class CellLine:
    """
    Generator iterable that returns cells of a particular row or column
    """
    sheet = None
    axis = None
    index = None
    i = 0
    highest_inhabited_i = -1
    # max_i = 0

    def __init__(self, sheet, axis, index):
        assert axis in ('x', 'y')
        self.sheet = sheet
        self.axis = axis
        self.index = index

    def __iter__(self):
        return self

    def __next__(self):
        x, y = (self.index, self.i) if self.axis == 'y' else \
            (self.i, self.index)
        cell = Cell(self.sheet, (x, y))
        if cell.string == '' and self.i > self.highest_inhabited_i:
            for x in range(1, MAX_CELL_GAP):
                test_x, test_y = (self.index, self.i + x) if \
                    self.axis == 'y' else (self.i + x, self.index)
                test_cell = Cell(self.sheet, position=(test_x, test_y))
                if test_cell.string != '':
                    self.highest_inhabited_i = self.i + x
                    break
            else:
                raise StopIteration()
        self.i += 1
        return cell


class Cell:
    """
    Handles usage of an individual cell
    """
    def __init__(self, sheet, position):
        assert all([isinstance(item, int) for item in position])
        assert len(position) == 2
        self.position = tuple(position)
        self.sheet = sheet

    def set_color(self, color):
        """
        Sets cell background color
        :param color: int, list or tuple
        """
        assert isinstance(color, (int, tuple, list))
        if isinstance(color, int):
            color_int = color
        else:
            color_int = color[0]*256**2 + color[1]*256 + color[2]
        self._source_cell.CellBackColor = color_int

    @property
    def _source_cell(self):
        """
        Gets PyUno cell from which values are drawn
        :return:
        """
        return self.sheet.getCellByPosition(*self.position)

    @property
    def value(self):
        """
        Gets value of cell.
        :return: str or float
        """
        # get cell value type after formula evaluation has been carried out
        # this will return the cell value's type even if it is not a formula
        t = self._source_cell.FormulaResultType.value
        if t == 'TEXT':
            return self._source_cell.getString()
        elif t == 'VALUE':
            return self._source_cell.getValue()

    @value.setter
    def value(self, new_value):
        """
        Sets source cell string and number value appropriately for
        a new value.
        This does not handle formulas at the present time.
        :param new_value: int, float, or str
        """
        assert isinstance(new_value, (str, int, float))
        if isinstance(new_value, str):
            self.float = 0
            self.string = new_value
        else:
            self.float = new_value
            self.string = str(new_value)

    @property
    def string(self):
        """
        Returns string value directly from source cell
        :return: str
        """
        return self._source_cell.getString()

    @string.setter
    def string(self, new_string):
        """
        Sets string value of source cell directly
        :param new_string: str
        """
        assert isinstance(new_string, str)
        self._source_cell.setString(new_string)

    @property
    def float(self):
        """
        Returns float value directly from source cell 'value'
        :return: float
        """
        return self._source_cell.getValue()

    @float.setter
    def float(self, new_value):
        """
        Sets float value of source cell directly
        :param new_value:
        :return:
        """
        assert isinstance(new_value, (int, float))
        new_value = float(new_value)
        self._source_cell.setValue(new_value)

    @property
    def x(self):
        """
        Gets x position of cell
        :return: int
        """
        return self.position[0]

    @property
    def y(self):
        """
        Gets y position of cell
        :return: int
        """
        return self.position[1]

    def __str__(self):
        return 'Cell[(%s), Value: %s' % (self.position, self.value)

###############################################################################
# Column Data


class Translation:
    """
    Handles movement of data from source to target sheets and applies
    modifications
    """
    def __init__(self,
                 source_sheet,
                 target_sheet,
                 column_translations=None,
                 row_deletions=None,
                 source_start_row=1,
                 target_start_row=1,
                 confirm_dialog_func=None):
        assert isinstance(source_sheet, Sheet)
        assert isinstance(target_sheet, Sheet)
        self._source_sheet = source_sheet
        self._target_sheet = target_sheet
        self._column_translations = column_translations if \
            column_translations else set()
        self._row_deletions = row_deletions if row_deletions else set()
        self._src_cell_transforms = {}
        self._tgt_cell_transforms = {}
        self._source_start_row = source_start_row
        self._target_start_row = target_start_row
        self.confirm_dialog_func = confirm_dialog_func

    def add_column_translation(self, source, target):
        """
        Adds translation to queue.
        When applied, copies cell data from source column to
        target column.
        :param source: int or str
        :param target: int or str
        """
        assert isinstance(source, (int, str))
        assert isinstance(target, (int, str))
        # get source x integer
        if isinstance(source, int):
            source_x = source
        else:
            source_x = self._source_sheet.get_column(source)
        # get target x integer
        if isinstance(target, int):
            target_x = target
        else:
            target_x = self._target_sheet.get_column(target)
        # append translation
        self._column_translations.add(ColumnTranslation(
            source_column=source_x, target_column=target_x
        ))

    def add_row_deletion(self, row):
        """
        Adds row deletion to queue
        :param row: int
        """
        assert isinstance(row, int)
        self._row_deletions.add(row)

    def add_cell_transform(self, pos, sheet, func):
        """
        Adds cell transformation to queue
        :param sheet: str, 'src' or 'tgt'
        :param pos: int x, int y
        :param func: function
        """
        assert isinstance(sheet, str) and sheet in ('src', 'tgt')
        assert isinstance(pos[0], int)
        assert isinstance(pos[1], int)
        assert hasattr(func, '__call__')
        transform = CellTransform(pos, sheet, func)
        if sheet == 'src':
            if pos not in self._src_cell_transforms:
                self._src_cell_transforms[pos] = list()
            self._src_cell_transforms[pos].append(transform)
        else:
            if pos not in self._tgt_cell_transforms:
                self._tgt_cell_transforms[pos] = []
            self._tgt_cell_transforms[pos].append(transform)

    def clear_cell_transform(self, pos, sheet):
        """
        Clears cell transforms from position
        :param pos: int x, int y
        :param sheet: 'src' or 'tgt'
        """
        assert isinstance(sheet, str) and sheet in ('src', 'tgt')
        assert isinstance(pos[0], int)
        assert isinstance(pos[1], int)
        if sheet == 'src' and pos in self._src_cell_transforms:
            del self._src_cell_transforms[pos]
        elif sheet == 'tgt' and pos in self._tgt_cell_transforms:
            del self._tgt_cell_transforms[pos]

    def commit(self):
        """
        Moves column from source to target and applies modifications
        applies each translation
        :return: bool of whether commit was applied or not
        """
        # clear data
        self.clear_target()

        # move data
        for column_translation in self._column_translations:
            row_i = self._target_start_row
            for source_cell in self._source_sheet.get_column(
                column_translation.source_column):
                # don't include source cells before start row
                # and whose y position is in deletion set.
                if source_cell.y in self._row_deletions or \
                        source_cell.y < self._source_start_row:
                    continue
                assert isinstance(source_cell, Cell)
                target_x = column_translation.target_column
                target_y = row_i + self.target_start_row - \
                    self.source_start_row
                # print('target start row: %s' % self.target_start_row)
                assert isinstance(target_x, int)
                assert isinstance(target_y, int)
                target_cell = self._target_sheet.get_cell((target_x,
                                                           target_y))
                assert isinstance(target_cell, Cell), target_cell
                target_cell.value = source_cell.value
                # apply cell transforms
                if source_cell.position in self._src_cell_transforms:
                    [transform(target_cell) for transform in
                     self._src_cell_transforms[source_cell.position]]
                if target_cell.position in self._tgt_cell_transforms:
                    [transform(target_cell) for transform in
                     self._tgt_cell_transforms[target_cell.position]]
                row_i += 1

        return True

    def clear_target(self):
        """
        Clears target sheet of conflicting cell data
        Raises dialog for user to ok if anything is to be deleted.
        """
        user_ok = False  # whether user has been presented with dialog
        for column in self._target_sheet.columns:
            assert isinstance(column, Column)
            for cell in column:
                if cell.y < self._target_start_row:
                    continue
                if not user_ok and cell.value != '':
                    # if user has not yet ok'd deletion of cells:
                    if self.confirm_dialog_func:
                        print('confirm dlg')
                        proceed = self.confirm_dialog_func()
                        if not proceed:
                            return False
                    user_ok = True
                cell.value = ''
                cell.set_color(DEFAULT_COLOR)

    @property
    def source_start_row(self):
        """
        Sets the row index at which cells begin to be copied.
        0 is first row
        :return: int
        """
        return self._source_start_row

    @source_start_row.setter
    def source_start_row(self, new_index):
        """
        Sets the row index at which cells begin to be copied
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._source_start_row = new_index

    @property
    def target_start_row(self):
        """
        Gets the row index at which cells begin to be written to
        :return: int
        """
        return self._target_start_row

    @target_start_row.setter
    def target_start_row(self, new_index):
        """
        Sets the row index at which cells begin to be written to
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._target_start_row = new_index

    @property
    def column_translations(self):
        """
        Returns list of column translations
        :return: list of ColumnTranslations
        """
        return self._column_translations.copy()


class ColumnTranslation:
    """
    Handles movement and modification of a column
    """
    def __init__(self, source_column, target_column):
        assert isinstance(source_column, int)
        assert isinstance(target_column, int)
        self._target_column = target_column
        self._source_column = source_column
        
    @property
    def target_column(self):
        """
        Gets target column
        :return: int
        """
        return self._target_column
    
    @target_column.setter
    def target_column(self, new_column):
        """
        Sets target column
        :param new_column: int
        """
        assert isinstance(new_column, int)
        self._target_column = new_column
    
    @property
    def source_column(self):
        """
        Gets source column
        :return: int
        """
        return self._source_column

    @source_column.setter
    def source_column(self, new_column):
        """
        Sets source column
        :param new_column: int
        """
        assert isinstance(new_column, int)
        self._source_column = new_column


class CellTransform:
    def __init__(self, position, sheet, call_obj):
        assert all([isinstance(x, int) for x in position])
        assert sheet in ('src', 'tgt')
        assert hasattr(call_obj, '__call__')
        self.position = position
        self.sheet = sheet
        self.call_obj = call_obj

    def __call__(self, cell):
        self.call_obj(cell)


###############################################################################
# GUI elements

class TranslationDialog(QtW.QWidget):
    """
    Table widget containing columns and options to manipulate them
    """
    def __init__(self,
                 source_sheet,
                 target_sheet,
                 target_start,
                 source_start,
                 prior_widget=None):
        print('Translation Dlg began')
        super().__init__()
        assert isinstance(source_sheet, (Sheet, str, int)), source_sheet
        assert isinstance(target_sheet, (Sheet, str, int)), target_sheet
        assert isinstance(source_start, (int, str)), source_start
        assert isinstance(target_start, (int, str)), target_start
        # widget to return to if back is clicked
        self.prior_widget = prior_widget
        # get Sheet obj from name or index if needed
        if not isinstance(source_sheet, Sheet):
            source_sheet = model[source_sheet]
        if not isinstance(target_sheet, Sheet):
            target_sheet = model[target_sheet]
        # get integer from string indices if needed.
        # checking to ensure strings are convertible should have already
        # taken place.
        if not isinstance(source_start, int):
            source_start = int(source_start)
        if not isinstance(target_start, int):
            target_start = int(target_start)
        self.source_sheet = source_sheet  # sheet to retrieve data from
        self.target_sheet = target_sheet  # sheet to send data to
        self.source_start_row = source_start
        self.target_start_row = target_start
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.show()

        def ok():
            """Function to confirm selections and create Translation"""
            self.table.store_settings()
            self.setWindowTitle('')  # free up window title
            final_settings = self.settings
            final_settings['prior_widget'] = self
            FinalSettings(**final_settings)
            self.hide()

        def back():
            """Function to resume prior dialog and close self"""
            self.setWindowTitle('')  # free up title
            self.prior_widget.resume()
            self.close()

        self.table = self.TranslationTable(
            self._get_source_columns(),
            self._get_target_columns())

        # build layouts
        main_layout = QtW.QVBoxLayout()
        confirm_bar = QtW.QHBoxLayout()
        confirm_bar.addWidget(BackButton(back))
        confirm_bar.addWidget(OkButton(ok))
        main_layout.addWidget(self.table)
        main_layout.addItem(confirm_bar)
        self.setLayout(main_layout)

    def resume(self):
        """Resumes current widget's use"""
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.show()

    def _get_source_columns(self):
        """
        Returns list of source column names
        :return: list
        """
        assert isinstance(self.source_sheet, Sheet)
        return [cell.value for cell in self.source_sheet.get_row(0)]

    def _get_target_columns(self):
        """
        Returns list of target column names
        :return: list
        """
        assert isinstance(self.target_sheet, Sheet)
        return [cell.value for cell in self.target_sheet.get_row(0)]

    class TranslationTable(QtW.QTableWidget):
        def __init__(self, source_columns, target_columns):
            super().__init__()
            assert isinstance(source_columns, (list, tuple))
            assert isinstance(target_columns, (list, tuple))
            assert all([isinstance(column, str) for column in source_columns])
            assert all([isinstance(column, str) for column in target_columns])
            self.source_columns = source_columns
            self.target_columns = target_columns
            self.option_widget_classes = [
                self.SourceColumnDropDown,
                self.WhiteSpaceCheckbox,
                self.DuplicateCheckbox
            ]
            self.draw_table()

        class SourceColumnDropDown(QtW.QComboBox):
            name = 'Source Column'
            dict_name = 'src column'

            def __init__(self, table, start_value=NONE_STRING):
                super().__init__()
                self.table = table
                self.setToolTip('Select column to use as source')
                self.addItems(table.source_columns + [NONE_STRING])
                self.setCurrentText(start_value)
                # todo: add margins?

            @property
            def value(self):
                return self.currentText()

        class WhiteSpaceCheckbox(QtW.QCheckBox):
            name = 'Check for Whitespace'
            dict_name = 'whitespace chk'

            def __init__(self, table, start_value=True):
                super().__init__()
                self.table = table
                self.setToolTip('Set whether whitespace is checked for in '
                                'this column')
                self.setChecked(start_value)

            @property
            def value(self):
                return self.isChecked()

        class DuplicateCheckbox(QtW.QCheckBox):
            name = 'Check for Duplicates'
            dict_name = 'duplicate chk'

            def __init__(self, table, start_value=True):
                self.table = table
                super().__init__()
                self.setToolTip('Set whether duplicate values are checked for '
                                'in this column')
                self.setChecked(start_value)

            @property
            def value(self):
                return self.isChecked()

        def draw_table(self):
            """Draws table, populates columns, sets visual settings"""
            self.setRowCount(len(self.target_columns))
            # set columns to number of options for each column
            self.setColumnCount(len(self.option_widget_classes))
            self.setAlternatingRowColors(True)
            # set row titles
            [self.setVerticalHeaderItem(y, QtW.QTableWidgetItem(column)) for
             y, column in enumerate(self.target_columns)]
            # set option column titles
            [self.setHorizontalHeaderItem(x, QtW.QTableWidgetItem(option.name))
             for x, option in enumerate(self.option_widget_classes)]
            # populate table
            for y in range(len(self.target_columns)):
                for x, option_class in enumerate(self.option_widget_classes):
                    self.setCellWidget(y, x, option_class(
                            table=self  # pass ref to self for use if needed
                        ))
            self.resizeColumnsToContents()

        def store_settings(self):
            """Saves settings for re-use"""
            # todo

        @property
        def settings(self):
            """
            Returns dictionary of column settings
            Returned dictionary is a dictionary of dictionaries.
            First dictionary has target column title as key.
            Second level dictionaries have setting name as key.
            :return: dict
            """
            return {column_name:
                    {self.cellWidget(y, x).dict_name:
                     self.cellWidget(y, x).value
                     for x in range(0, len(self.option_widget_classes))}
                    for y, column_name in enumerate(self.target_columns)}

    @property
    def settings(self):
        """
        Returns settings dictionary
        :return: dict
        """
        return {
            'table': self.table.settings,
            'source_sheet': self.source_sheet,
            'target_sheet': self.target_sheet,
            'source_start': self.source_start_row,
            'target_start': self.target_start_row
        }


class PreliminarySettings(QtW.QWidget):
    class SettingField(QtW.QLineEdit):
        # string appearing next to field in settings table
        side_string = ''  # replaced by child classes
        # name under which to store field str
        dict_string = ''  # replaced by child classes
        # values to default to, in order of priority
        default_strings = tuple()  # replaced by child classes

        def __init__(self, start_str='', default_values=None):
            assert isinstance(start_str, str)
            assert default_values is None or \
                   isinstance(default_values, (tuple, list))
            super().__init__()
            self.start_str = start_str
            # add default values -before- standard defaults (order matters)
            if default_values:
                self.default_strings = default_values + \
                                       tuple(self.defaults)
            # set text to default value
            self.setText(self._find_default_value())
            self.gui_setup()
            self.show()

        def _find_default_value(self):
            pass  # does nothing here.

        def gui_setup(self):
            pass  # does nothing here, inherited by child classes

        def check_valid(self):
            pass  # inherited

    class SheetField(SettingField):
        def _find_default_value(self):
            # find default value
            if self.start_str:  # if a starting string has been passed,
                # use that.
                self.setText(self.start_str)
            else:  # otherwise, find the first default value that works
                # for each sheet of both passed and native defaults,
                # check if they exist, if so, use that value
                existing_sheet = model.sheet_exists(*self.default_strings)
                if existing_sheet:
                    return existing_sheet
                else:
                    return ''

    class ImportSheetField(SheetField):
        """Gets name of sheet to import from"""
        dict_string = 'source_sheet'
        side_string = 'Import sheet name'
        default_strings = 'import', 'Sheet1', 'sheet1'

        def gui_setup(self):
            self.setToolTip('Sheet to import columns from')
            self.setPlaceholderText('Import Sheet')

        def check_valid(self):
            sheet_name = self.text()  # get text entered by user
            assert isinstance(sheet_name, str)
            if model.sheet_exists(sheet_name):
                return True
            elif sheet_name == '':
                InfoMessage(
                    parent=self,
                    title='Field Left Blank',
                    main='Import sheet name left blank',
                    secondary='The name of the sheet to copy column data from '
                              'must be entered.'
                )
            else:
                InfoMessage(
                    parent=self,
                    title='Non-Existent Sheet',
                    main='Sheet does not exist',
                    secondary='Source sheet \'%s\' could not be found' %
                              sheet_name
                )

    class ExportSheetField(SheetField):
        """Gets name of sheet to export to"""
        dict_string = 'target_sheet'
        side_string = 'Export sheet name'
        default_strings = 'export', 'Sheet2', 'sheet2'

        def gui_setup(self):
            self.setToolTip('Sheet to export columns to')
            self.setPlaceholderText('Export Sheet')

        def check_valid(self):
            sheet_name = self.text()  # get text entered by user
            assert isinstance(sheet_name, str)
            if model.sheet_exists(sheet_name):
                return True
            elif sheet_name == '':
                InfoMessage(
                    parent=self,
                    title='Field Left Blank',
                    main='Export sheet name left blank',
                    secondary='The name of the sheet to copy column data to '
                              'must be entered.'
                )
            else:
                InfoMessage(
                    parent=self,
                    title='Non-Existent Sheet',
                    main='Sheet does not exist',
                    secondary='Target sheet \'%s\' could not be found' %
                              sheet_name
                )

    class StartLineField(SettingField):
        default_strings = '1',

        def _find_default_value(self):
            return self.default_strings[0]  # until a better method is
            # available

        def check_valid(self):
            if self.text() == '':
                self._invalid_row('%s cannot be blank.' % self.side_string)
            elif not self.text().isdigit():
                self._invalid_row('Value entered for %s ( %s ) does '
                                  'not appear to be an integer.' %
                                  (self.side_string, self.text()))
            elif self.value < 0:
                self._invalid_row('%s cannot be negative. Got: %s.' %
                                  (self.side_string, self.value))
            else:
                return True

        def _invalid_row(self, explain_str):
            InfoMessage(
                parent=self,
                title='Invalid Row Index',
                main='Entered row is invalid.',
                secondary=explain_str
            )

        @property
        def value(self):
            """
            Gets user entered value
            :return: int
            """
            return int(self.text())

    class ImportSheetStartLine(StartLineField):
        """Gets index of line to start importing from"""
        dict_string = 'source_start'
        side_string = 'Import sheet start line'

        def gui_setup(self):
            self.setToolTip('Index of first row to be imported')
            self.setPlaceholderText('Import start row')

    class ExportSheetStartLine(StartLineField):
        """Gets index of line to start writing to"""
        dict_string = 'target_start'
        side_string = 'Export sheet start line'

        def gui_setup(self):
            self.setToolTip('Index of first row to be written to on target '
                            'sheet')
            self.setPlaceholderText('Export start row')

    class CancelButton(QtW.QPushButton):
        """Cancels out of macro"""
        def __init__(self):
            super().__init__()
            self.setText('Cancel')
            self.clicked.connect(self._cancel)
            self.show()

        def _cancel(self):
            """
            Cancels out of macro.
            """
            # exit macro, without exiting EVERYTHING
            QtW.QApplication.quit()  # not an error, doesn't need self arg
            # (lesson learned: don't use 'quit' / SystemExit in a macro)

    def __init__(self, starting_dictionary=None):
        print('Preliminary Dlg began')
        super().__init__()
        # values of fields, may be passed in if user has previously
        # entered settings, or is perhaps loading existing settings
        values = starting_dictionary if starting_dictionary else {}

        # define fields to be in preliminary settings widget
        field_classes = (
            self.ImportSheetField,
            self.ExportSheetField,
            self.ImportSheetStartLine,
            self.ExportSheetStartLine
        )  # one of each of these will be instantiated in the grid

        # create grid
        grid = ExpandingGridLayout()
        self.setLayout(grid)

        # create fields; add one instance of each field class
        self.fields = []
        print('began field creation')
        for x, field_class in enumerate(field_classes):
            dict_str = field_class.dict_string
            start_str = '' if dict_str not in values else values[dict_str]

            # todo: additional defaults should be found and added here
            # in the future
            additional_default_values = []

            # create and add the field
            field = field_class(start_str=start_str,
                                default_values=additional_default_values)
            assert isinstance(field, self.SettingField)
            self.fields.append(field)
            grid.add_row(field.side_string, field)
        # add ok and cancel buttons
        grid.add_row(self.CancelButton(), OkButton(self._ok))
        # todo: limit / freeze size of window
        self.setWindowTitle(APP_WINDOW_TITLE)
        print('finished creating, showing.')
        self.show()

    def _ok(self):
        """
        Method called when user clicks 'ok' button on Preliminary
        Settings Widget.
        Creates AssociationTableWidget and passes it the created
        settings dictionary.
        """
        values_dict = self.get_values_dict()
        # check that entered sheets exist
        if any([not field.check_valid() for field in self.fields]):
            # field.check_valid displays info dialogs to user
            # if not valid.
            return  # does not move on if any fields are not valid
        self.setWindowTitle('')  # allow next widget to use the same title
        values_dict['prior_widget'] = self
        TranslationDialog(**values_dict)  # create next widget
        self.hide()  # hide self until returned to or macro ends

    def resume(self):
        """
        Returns this widget to activity after user returns to it.
        This most likely means the user has hit clicked 'back' on
        the following widget
        :return:
        """
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.show()

    def get_values_dict(self):
        """
        Gets dictionary of values stored in each field
        :return: dict
        """
        return {field.dict_string: field.text() for field in self.fields}


class FinalSettings(QtW.QWidget):
    def __init__(self, **kwargs):
        print('Final Settings dlg began')
        super().__init__()
        self.prior_widget = kwargs.get('prior_widget')
        self._settings = kwargs
        # del self.settings['prior_widget']

        field_classes = [
            self.DuplicateActionOption,
            self.WhitespaceOption,
        ]

        def back():
            self.setWindowTitle('')  # free up title
            self.prior_widget.resume()
            self.close()

        layout = ExpandingGridLayout()
        self.fields = []  # list of fields for user to input/select strings
        for field_class in field_classes:
            field = field_class()
            layout.add_row(field_class.side_string, field)
            self.fields.append(field)
        layout.add_row(BackButton(back), self.ApplyButton(self))
        self.setLayout(layout)
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.show()

    class ApplyButton(QtW.QPushButton):
        def __init__(self, host):
            assert isinstance(host, FinalSettings)
            super().__init__()

            def apply():
                """
                Builds translation object and passes it to FinalAction
                """
                # todo: this whole function is ridiculous. break it up?
                # get settings
                settings = host.settings
                src_sheet = settings['source_sheet']
                tgt_sheet = settings['target_sheet']
                assert isinstance(src_sheet, Sheet)
                assert isinstance(tgt_sheet, Sheet)
                # make translation obj

                def delete_confirm():
                    reply = QtW.QMessageBox.question(
                        self,
                        'Overwrite Cells?',
                        'Cells on the target sheet will be overwritten.\n'
                        'Proceed?',
                        QtW.QMessageBox.Yes | QtW.QMessageBox.Cancel,
                        QtW.QMessageBox.Cancel
                    )
                    return reply == QtW.QMessageBox.Yes

                translation = Translation(
                    src_sheet,
                    tgt_sheet,
                    source_start_row=settings['source_start'],
                    target_start_row=settings['target_start'],
                    confirm_dialog_func=delete_confirm
                )

                # make column translations
                table_set = settings['table']

                duplicate_positions = set()
                whitespace_positions = set()
                for tgt_col_name in table_set:
                    col_settings = table_set[tgt_col_name]
                    src_col_name = col_settings['src column']
                    if src_col_name == NONE_STRING:
                        continue
                    src_col = src_sheet.get_column(src_col_name)
                    assert isinstance(src_col, Column)
                    src_col_index = src_col.column_index
                    tgt_col = tgt_sheet.get_column(tgt_col_name)
                    tgt_col_index = tgt_col.column_index
                    translation.add_column_translation(
                        src_col_index, tgt_col_index)
                    # find duplicates / whitespace
                    if col_settings['duplicate chk'] and \
                           settings['duplicate_action'] != 'Do nothing':
                        cell_value_set = set()
                        for cell in src_col:
                            if cell.y < settings['source_start']:
                                continue
                            if cell.value in cell_value_set:
                                duplicate_positions.add(cell.position)
                            else:
                                cell_value_set.add(cell.value)
                    if col_settings['whitespace chk'] and \
                            settings['whitespace_action'] != 'Do nothing':
                        for cell in src_col:
                            # check if cell value is string and has whitespace
                            if isinstance(cell.value, str) and \
                                    cell.value != cell.value.strip():
                                whitespace_positions.add(cell.position)

                def color_cell_and_row(cell_pos, cell_color,
                                       row_color):
                    # mark all cells in row
                    [translation.add_cell_transform(
                        (x, cell_pos[1]),
                        'src',
                        lambda c: c.set_color(row_color)
                    ) for x in range(len(
                        src_sheet.get_row(cell_pos[1])))]
                    # mark cell with duplicate red1
                    translation.clear_cell_transform(
                        cell_pos, 'src')
                    translation.add_cell_transform(
                        cell_pos, 'src',
                        lambda c: c.set_color(cell_color))

                def position_report(*src_positions):
                    """
                    Converts iterable of positions into a more user-friendly
                    report.
                    output should consist of a list of row numbers, each with
                    the names of the column containing passed position
                    :param positions: tuples (int x, int y)
                    :return: str
                    """

                    def src_to_tgt_pos(src_pos_):
                        """
                        Converts src_pos to tgt_pos
                        :param src_pos_: int x, int y
                        :return: int x, int y
                        """

                        def find_col_translation(x_):
                            for col_transform in \
                                    translation.column_translations:
                                assert isinstance(col_transform,
                                                  ColumnTranslation)
                                if col_transform.source_column == x_:
                                    return col_transform

                        # find column the x index will be moved to
                        # by looking through column transforms
                        x_translation = find_col_translation(
                            src_pos_[0])
                        assert isinstance(x_translation, ColumnTranslation)
                        tgt_x = x_translation.target_column
                        tgt_y = src_pos_[1] - translation.source_start_row + \
                            translation.target_start_row
                        return tgt_x, tgt_y

                    # first convert src positions to tgt positions
                    tgt_positions = [src_to_tgt_pos(src_pos_)
                                     for src_pos_ in src_positions]

                    rows = []  # list of row indices in report.
                    # This keeps the columns in order.
                    row_columns = {}  # dictionary of string lists
                    for x, y in tgt_positions:
                        column_name = tgt_sheet.get_column(x).name
                        if y not in rows:
                            row_columns[y] = list()
                            rows.append(y)
                        row_columns[y].append(column_name)
                    # now make the report
                    row_strings = [
                        'Row %s; %s' % (y, ', '.join(row_columns[y]))
                        for y in rows]
                    return '\n'.join(row_strings)

                print('dupli act: %s' % settings['duplicate_action'])
                print('whitespace act: %s' % settings['whitespace_action'])
                # apply response for duplicates
                if settings['duplicate_action'] == 'Highlight':
                    # highlight
                    for position in duplicate_positions:
                        color_cell_and_row(position, FIREBRICK, CORAL)
                    if len(duplicate_positions) > 0:
                        InfoMessage(
                            parent=self,
                            title='Duplicate Values',
                            main='%s Duplicate cell values found' % len(
                                duplicate_positions),
                            secondary='Cell values were highlighted in '
                                      'checked columns',
                            detail=position_report(*duplicate_positions)
                        )
                elif settings['duplicate_action'] == 'Remove row':
                    [translation.add_row_deletion(position[1])
                     for position in duplicate_positions]
                    if len(duplicate_positions)> 0:
                        n_rows_w_duplicates = len(set(
                            [pos[1] for pos in duplicate_positions]))
                        InfoMessage(
                            parent=self,
                            title='Duplicate Values',
                            main='%s Duplicate cell values found' %
                                 n_rows_w_duplicates,
                            secondary='%s Cell rows containing duplicate '
                                      'values were removed' %
                                      n_rows_w_duplicates,
                            detail=position_report(*duplicate_positions)
                        )
                # apply response to whitespace
                if settings['whitespace_action'] == 'Highlight':
                    [color_cell_and_row(pos, ORANGE, KHAKI)
                     for pos in whitespace_positions]
                    if len(whitespace_positions) > 0:
                        InfoMessage(
                            parent=self,
                            title='Whitespace Found',
                            main='%s Cells with unneeded whitespace found' %
                                 len(whitespace_positions),
                            secondary='%s Cell values were highlighted in '
                                      'checked '
                                      'columns' % len(whitespace_positions),
                            detail=position_report(*whitespace_positions)
                        )
                elif settings['whitespace_action'] == 'Remove whitespace':
                    def remove_whitespace(cell_position):
                        cell_ = src_sheet.get_cell(cell_position)
                        if isinstance(cell_.value, str):
                            cell_.value = cell_.value.strip()
                    [remove_whitespace(pos) for pos in whitespace_positions]
                    if whitespace_positions:
                        InfoMessage(
                            parent=self,
                            title='Whitespace Removed',
                            main='Whitespace removed from %s cells' % len(
                                whitespace_positions),
                            secondary='Cell values were edited to remove '
                                      'unneeded '
                                      'tab, linefeed, return, formfeed, '
                                      'and/or vertical tab characters.',
                            detail=position_report(*duplicate_positions)
                        )

                # apply translation
                success = translation.commit()
                # result is true if commit was successful
                if success:
                    InfoMessage(  # tell user translation has been applied
                        parent=self,
                        title='Macro Finished',
                        main='Finished moving cell values'
                    )
                    QtW.QApplication.quit()  # not an error. self not needed.

            self.clicked.connect(apply)
            self.setText('Apply')
            self.setToolTip('Apply selections & Move cells from source sheet '
                            'to target')

    class MenuOption(QtW.QComboBox):
        options = tuple()  # overridden by child classes
        default_option = ''
        tool_tip = ''
        dict_str = ''
        side_string = ''

        def __init__(self, start_value=None):
            super().__init__()
            self.addItems(self.options)
            self.setToolTip(self.tool_tip)
            self.setCurrentText(start_value if start_value else
                                self.default_option)
            # todo: add margins?

        @property
        def value(self):
            return self.currentText()

    class DuplicateActionOption(MenuOption):
        options = 'Do nothing', 'Highlight', 'Remove row'
        default_option = 'Highlight'
        tool_tip = 'Select action to be taken for rows containing ' \
                   'duplicate in checked columns'
        dict_str = 'duplicate_action'
        side_string = 'Action for duplicates'

    class WhitespaceOption(MenuOption):
        options = 'Do nothing', 'Highlight', 'Remove whitespace'
        default_option = 'Highlight'
        tool_tip = 'Select action to be taken for cells containing whitespace'
        dict_str = 'whitespace_action'
        side_string = 'Action for whitespace'

    @property
    def settings(self):
        """
        Returns grand collection of all settings inputted by user
        :return: dict
        """
        settings = self._settings
        [settings.__setitem__(option.dict_str, option.value)
         for option in self.fields]
        return settings


class InfoMessage(QtW.QMessageBox):
    """
    Displays simple information dialogue with title, main message,
    and secondary message beneath that.
    Icon is an Info 'I.'
    """
    def __init__(self, parent, title, main, secondary='', detail=''):
        assert all([isinstance(item, str)
                    for item in (title, main, secondary, detail)])
        super().__init__(parent)
        self.setIcon(QtW.QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(main)
        if secondary:
            self.setInformativeText(secondary)
        self.setStandardButtons(QtW.QMessageBox.Ok)
        if detail is not '':
            self.setDetailedText(detail)
        self.exec()


class ConfirmDialog(QtW.QMessageBox):
    """
    Dialog for user to accept or cancel
    """
    def __init__(self, parent, title, main, secondary=''):
        assert all([isinstance(item, str)
                    for item in (title, main, secondary)])
        super().__init__(parent)



        self.setWindowTitle(title)
        self.setText(main)
        if secondary:
            self.setInformativeText(secondary)
        self.setStandardButtons(QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
        self.setDefaultButton(QtW.QMessageBox.Ok)


class OkButton(QtW.QPushButton):
    """
    calls passed function when clicked by user.
    """
    def __init__(self, ok_function):
        super().__init__('OK')
        self.clicked.connect(ok_function)  # not error
        self.setToolTip('Move to next page')
        self.show()


class BackButton(QtW.QPushButton):
    def __init__(self, back_function):
        super().__init__('Back')
        self.setToolTip('Go to last page')
        self.clicked.connect(back_function)  # not error
        self.show()


class ExpandingGridLayout(QtW.QGridLayout):
    """
    Grid layout that can be simply expanded
    """

    def __init__(self):
        super().__init__()

    def add_row(self, *items):
        """
        Adds a row to the grid, consisting of the passed items
        :param items: items
        """
        y = self.rowCount()
        for x, item in enumerate(items):
            # convert string to label
            if isinstance(item, str):
                item = QtW.QLabel(item)
            self.addWidget(item, y, x)

###############################################################################
# SETTINGS / DATA


class Settings:
    def __init__(self, settings_file_path):
        print('created settings')
        self.file_path = settings_file_path

    @property
    def settings(self):
        # todo
        return dict()


def lead_app():
    """
    Main lead sheet management macro.
    Calls
    """
    # flow:
    # preliminary settings ->
    # association table ->
    # final settings / info
    # push data to target
    # close / display exit message
    print('started pyleadsmacro')
    print(sys.version_info)
    app = QtW.QApplication([''])  # expects list of strings.
    print('started app')

    try:
        # get settings path
        settings_path = ''  # placeholder. todo: get str, cross-platform
        # build and show first window
        settings = Settings(settings_path).settings
        prelim = PreliminarySettings(settings)  # get settings from prelim dialog

        sys.exit(app.exec_())
        # todo: refactor all the dialogs so they return to this point,
        # rather than forming a chain of one dialog calling the next
    except SystemExit:
        print('SystemExit raised')
        print('Exited macro')
        app.quit()
        # let macro exit without displaying an error


# create model handler object and in doing so,
# check PyUno model is a Workbook
model = Model(MODEL)
