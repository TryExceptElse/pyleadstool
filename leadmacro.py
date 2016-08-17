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
"""


import PyQt5.QtWidgets as QtW
import sys

DESKTOP = XSCRIPTCONTEXT.getDesktop()  # not an error; provided by macro caller
MODEL = DESKTOP.getModel()

ZERO_CHARACTERS = '0$,.-'  # chars that may appear in a zero valued float cell
MAX_CELL_GAP = 10  # max distance between inhabited cells in the workbook

APP_WINDOW_TITLE = 'Lead Macro'
DEFAULT_WIDGET_X = 512
DEFAULT_WIDGET_Y = 512
DEFAULT_WIDGET_H = 512
DEFAULT_WIDGET_W = 1024

STANDARD_GRID_SPACING = 10


###############################################################################
# Model Classes / PyUno class handling


class Model:
    """
    Handles usages of PyUno Model
    """
    def __init__(self, py_uno_model):
        assert hasattr(py_uno_model, 'Sheets')
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
        return self.sheet.getCellByIndex(*position)

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
            return self.sheet.getCellByIndex(self.column_index,
                                             cell_identifier)
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
    max_i = 0

    def __init__(self, sheet, axis, index):
        assert axis in 'x', 'y'
        self.sheet = sheet
        self.axis = axis
        self.index = index

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.max_i:
            raise StopIteration()
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

    @property
    def _source_cell(self):
        """
        Gets PyUno cell from which values are drawn
        :return:
        """
        return self.sheet.getCellByIndex(*self.position)

    @property
    def value(self):
        """
        Gets value of cell
        Since the interface with the spreadsheet makes it hard to
        determine what the type is of a cell whose value is produced
        via formula and whose number value is 0;
        this returns a 'best guess' for formula-type cells, determined
        by whether the cell's string value contains only number and
        number related characters.
        :return: str or float
        """
        # todo: check cell type first
        source_value = self._source_cell.getValue()
        source_string = self._source_cell.getString()
        if source_value != 0:
            return source_value
        else:  # really need a better way to determine type
            if any([char not in ZERO_CHARACTERS for char in source_string]):
                return source_string
            else:
                return source_value

    @value.setter
    def value(self, new_value):
        """
        Sets source cell string and number value appropriately for
        a new value
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
                 target_start_row=1):
        assert isinstance(source_sheet, Sheet)
        assert isinstance(target_sheet, Sheet)
        self._source_sheet = source_sheet
        self._target_sheet = target_sheet
        self._column_translations = column_translations if \
            column_translations else set()
        self._row_deletions = row_deletions if row_deletions else []
        self._source_start_row = source_start_row
        self._target_start_row = target_start_row

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
        self._column_translations.append(ColumnTranslation(
            source_column=source_x, target_column=target_x
        ))

    def add_row_deletion(self, row):
        """
        Adds row deletion to queue
        :param row: int
        """
        assert isinstance(row, int)
        self._row_deletions.add(row)


    def commit(self):
        """
        Moves column from source to target and applies modifications
        applies each translation
        """
        for column_translation in self._column_translations:
            row_i = self._target_start_row
            for source_cell in column_translation.source_column:
                # don't include source cells before start row
                # and whose y position is in deletion set.
                if source_cell.y not in self._row_deletions and \
                        source_cell.y >= self._source_start_row:
                    target_x = column_translation.target_column
                    target_y = row_i + self.target_start_row
                    assert isinstance(target_x, int)
                    assert isinstance(target_y, int)
                    target_cell = self._target_sheet.get_cell((target_x,
                                                               target_y))
                    assert isinstance(target_cell, Cell)
                    target_cell.value = source_cell.value
                    row_i += 1

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


###############################################################################
# GUI elements

class LeadWidget(QtW.QWidget):
    """
    Main widget
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(DEFAULT_WIDGET_X,
                         DEFAULT_WIDGET_Y,
                         DEFAULT_WIDGET_W,
                         DEFAULT_WIDGET_H)
        self.show()


class AssociationTable(QtW.QTableWidget):
    """
    Table widget containing columns and options to manipulate them
    """
    def __init__(self,
                 source_sheet,
                 target_sheet,
                 target_start_row,
                 source_start_row,
                 prior_widget=None):
        super().__init__()
        # widget to return to if back is clicked
        self.prior_widget = prior_widget
        self.source_sheet = source_sheet  # sheet to retrieve data from
        self.target_sheet = target_sheet  # sheet to send data to
        self.source_start_row = source_start_row
        self.target_start_row = target_start_row
        # set header row
        self.source_list = [cell for cell in source_sheet.reference_row]
        self.redraw()

    def redraw(self):
        """Draws table based on entries in source list"""
        # update table size
        self.setRowCount(len(self.source_list))
        self.setColumnCount(5)
        for x, cell in enumerate(self.source_list):
            # set the title row
            self.setItem(0, x, QtW.QTableWidgetItem(cell.string))
            # set alias for column
            self.setItem(1, x, ColumnAliasEdit(cell.string))
            # set the row of column move buttons below the title row
            self.setItem(2, x, MoveColumnButtonPair(self, x))
            # set delete buttons
            self.setItem(3, x, DeleteColumnButton(self, x))
            # duplicate check CheckBox
            self.setItem(4, x, DuplicateCheckBox())


class MoveColumnButtonPair(QtW.QWidget):
    def __init__(self, table_widget, index):
        self.table_widget = table_widget
        self.index = index
        super().__init__()

        layout = QtW.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(LeftColumnMoveButton(table_widget, index))
        layout.addWidget(RightColumnMoveButton(table_widget, index))

        self.setLayout(layout)


class ColumnButton(QtW.QPushButton):
    # may be obsolete
    def __init__(self, table_widget, index):
        assert isinstance(table_widget, AssociationTable)

        super().__init__()
        self.table_widget = table_widget
        self.index = index
        self.clicked.connect(self.handle_click)  # this is supposed to work?

    def handle_click(self):
        pass  # handled in child objects


class LeftColumnMoveButton(ColumnButton):
    # may be obsolete
    def __init__(self, table_widget, index):
        super().__init__(table_widget, index)
        self.setText('<-')  # todo: icon
        self.setToolTip('Move column left')

    def handle_click(self):
        lst = self.table_widget.source_list
        lst[self.index - 1], lst[self.index] = \
            lst[self.index], lst[self.index - 1]
        self.table_widget.redraw()


class RightColumnMoveButton(ColumnButton):
    # may be obsolete
    def __init__(self, table_widget, index):
        super().__init__(table_widget, index)
        self.setText('->')  # todo: icon
        self.setToolTip('Move column right')

    def handle_click(self):
        lst = self.table_widget.source_list
        lst[self.index], lst[self.index + 1] = \
            lst[self.index + 1], lst[self.index]
        self.table_widget.redraw()


class DeleteColumnButton(ColumnButton):
    def __init__(self, table_widget, index):
        super().__init__(table_widget, index)
        self.setText('Delete')
        self.setToolTip('Deletes column from table')

    def handle_click(self):
        self.table_widget.source_list.pop(self.index)


class DuplicateCheckBox(QtW.QCheckBox):
    """Checkbox denoting whether column should be checked for duplicates"""
    def __init__(self):
        super().__init__()
        self.setText('Duplicate Check')
        self.setToolTip('Checks all cells of this column for duplicates')
        self.setChecked(True)


class ColumnAliasEdit(QtW.QLineEdit):
    """Field for entering name under which column should be stored"""
    def __init__(self, default_text=''):
        super().__init__()
        self.setText(default_text)
        self.setPlaceholderText('Export Name')
        self.setToolTip('New name which column will appear as')


class PreliminarySettings(QtW.QWidget):
    class SheetField(QtW.QLineEdit):
        # string appearing next to field in settings table
        side_string = ''  # replaced by child classes
        # name under which to store field str
        dict_string = ''  # replaced by child classes
        # values to default to, in order of priority
        default_values = tuple()  # replaced by child classes
        def __init__(self, start_str='', default_values=None):
            assert isinstance(start_str, str)
            assert default_values is None or \
                   isinstance(default_values, (tuple, list))
            super().__init__()
            self.start_str = start_str
            # add default values -before- standard defaults (order matters)
            if default_values:
                self.default_values = default_values + \
                                      tuple(self.default_values)
            # set text to default value
            self.setText(self._find_default_value())
            self._gui_setup()
            self.show()

        def _find_default_value(self):
            # find default value
            if self.start_str:  # if a starting string has been passed, use that.
                self.setText(self.start_str)
            else:  # otherwise, find the first default value that works
                # for each sheet of both passed and native defaults,
                # check if they exist, if so, use that value
                existing_sheet = model.sheet_exists(*self.default_values)
                if existing_sheet:
                    return existing_sheet
                else:
                    return ''

        def gui_setup(self):
            pass  # does nothing here, inherited by child classes

        def check_valid(self):
            pass  # inherited

    class ImportSheetField(SheetField):
        dict_string = 'import'
        side_string = 'Import sheet name'
        default_values = 'import', 'Sheet1', 'sheet1'
        def gui_setup(self):
            self.setToolTip('Sheet to import columns from')
            self.setPlaceholderText('Import Sheet')

        def check_valid(self):
            sheet_name = self.
            assert isinstance(sheet_name, str)
            if model.sheet_exists(sheet_name):
                return True
            else:
                InfoMessage(
                    title='Non-Existent Sheet',
                    main='Sheet does not exist',
                    secondary='Source sheet \'%s\' could not be found' %
                        sheet_name
                )

    class ExportSheetField(SheetField):
        dict_string = 'export'
        side_string = 'Export sheet name'
        default_values = 'export', 'Sheet2', 'sheet1'
        def gui_setup(self):
            self.setToolTip('Sheet to export columns to')
            self.setPlaceholderText('Export Sheet')

        def check_valid(self):
            sheet_name = self.
            assert isinstance(sheet_name, str)
            if model.sheet_exists(sheet_name):
                return True
            else:
                InfoMessage(
                    title='Non-Existent Sheet',
                    main='Sheet does not exist',
                    secondary='Target sheet \'%s\' could not be found' %
                              sheet_name
                )

    class CancelButton(QtW.QPushButton):
        def __init__(self):
            super().__init__()
            self.setText('Cancel')
            self.clicked.connect()
            self.show()

        def _cancel(self):
            """
            Cancels out of macro.
            """
            quit()

    class OkButton(QtW.QPushButton):
        def __init__(self, ok_function):
            super().__init__('OK')
            self.clicked.connect(ok_function)
            self.show()


    def __init__(self, starting_dictionary=None):
        super().__init__()
        # values of fields, may be passed in if user has previously
        # entered settings, or is perhaps loading existing settings
        values = starting_dictionary if starting_dictionary else {}

        # define fields to be in preliminary settings widget
        field_classes = (
            self.ImportSheetField,
            self.ExportSheetField
        )

        # create grid
        grid = QtW.QGridLayout
        self.setLayout(grid)

        # create fields
        self.fields = []
        for field_class in field_classes:
            dict_str = field_class.dict_string
            start_str = '' if dict_str not in values else values[dict_str]

            # todo: additional defaults should be found and added here
            # in the future
            additional_default_values = []

            # create and add the field
            field = field_class(start_str=start_str,
                                default_values=additional_default_values)
            assert isinstance(field, self.SheetField)
            self.fields.append(field)
            grid.addRow(field.side_string, field)
        # add ok and cancel buttons
        grid.addRow(self.CancelButton(), self.OkButton(self._ok))
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
            return  # does not move on if any fields are not valid
        source_sheet = model[values_dict['import']]
        target_sheet = model[values_dict['export']]
        AssociationTable(  # create next widget
            source_sheet=source_sheet,
            target_sheet=target_sheet,
            prior_widget=self
        )
        self.hide()  # hide self until returned to or macro ends

    def resume(self):
        """
        Returns this widget to activity after user returns to it.
        This most likely means the user has hit clicked 'back' on
        the following widget
        :return:
        """
        self.show()

    def get_values_dict(self):
        """
        Gets dictionary of values stored in each field
        :return: dict
        """
        return {field.dict_string: field.getText() for field in self.fields}


class FinalSettings(QtW.QTableWidget):
    def __init__(self, starting_dictionary=None):
        values = starting_dictionary if starting_dictionary else {}
        # todo


class InfoMessage(QtW.QMessageBox):
    """
    Displays simple information dialogue with title, main message,
    and secondary message beneath that.
    Icon is an Info 'I.'
    """
    def __init__(self, title, main, secondary):
        super().__init__()
        self.setIcon(QtW.QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(main)
        self.setInformativeText(secondary)
        self.setStandardButtons(QtW.QMessageBox.Ok)
        self.show()


# create model handler object and in doing so,
# check PyUno model is a Workbook
model = Model(MODEL)


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
    app = QtW.QApplication(sys.argv)
    # build and show first window
    PreliminarySettings()  # get settings from preliminary dialog
