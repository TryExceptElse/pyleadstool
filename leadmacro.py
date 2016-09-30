"""
    ~
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

TODO:
skip empty column names on import sheet / export sheet
save/load column source table

INSTALL:
for libreoffice, requires python scripts module installed.
in ubuntu, this can be installed via
    'apt-get install libreoffice-script-provider-python'

"""

import pickle

import PyQt5.QtWidgets as QtW

import sys
import os
import platform

APP_FOLDER_NAME = 'leadsmacro'

MAX_CELL_GAP = 10  # max distance between inhabited cells in the workbook

APP_WINDOW_TITLE = 'Lead Macro'
DEFAULT_WIDGET_X = 512
DEFAULT_WIDGET_Y = 512
DEFAULT_WIDGET_H = 512
DEFAULT_WIDGET_W = 1024
DEFAULT_CONTENT_MARGIN_X = 15
DEFAULT_CONTENT_MARGIN_Y = 5

STANDARD_GRID_SPACING = 10

NONE_STRING = '< Empty >'

# colors #

DEFAULT_COLOR = -1
WHITE = 0xffffff
FIREBRICK = 0xB22222
CORAL = 0xFF7F50
ORANGE = 0xBDB76B
KHAKI = 0xF0E68C

WHITESPACE_CELL_COLOR = FIREBRICK
WHITESPACE_ROW_COLOR = CORAL
DUPLICATE_CELL_COLOR = ORANGE
DUPLICATE_ROW_COLOR = KHAKI

# Settings Keys #

SOURCE_SHEET_KEY = 'Source Sheet'
TARGET_SHEET_KEY = 'Target Sheet'
SOURCE_START_KEY = 'Source Start'
TARGET_START_KEY = 'Target Start'
DUPLICATE_ACTION_KEY = 'Duplicate Action'
WHITESPACE_ACTION_KEY = 'Whitespace Action'
COLUMN_TRANSLATIONS_KEY = 'Column Translations'

SOURCE_COLUMN_NAME_KEY = 'source_column_name'
TARGET_COLUMN_NAME_KEY = 'target_column_name'
SOURCE_COLUMN_INDEX_KEY = 'source_column_i'
TARGET_COLUMN_INDEX_KEY = 'target_column_i'
WHITESPACE_CHK_KEY = 'check_for_whitespace'
DUPLICATE_CHK_KEY = 'check_for_duplicates'

WHITESPACE_REMOVE_STR = 'delete'
WHITESPACE_HIGHLIGHT_STR = 'highlight'
WHITESPACE_IGNORE_STR = 'ignore'

DUPLICATE_REMOVE_ROW_STR = 'remove row'
DUPLICATE_HIGHLIGHT_STR = 'highlight'
DUPLICATE_IGNORE_STR = 'ignore'


###############################################################################
# BOOK INTERFACE


class Model:
    """
    Abstract model to be extended by office interface specific
    subclasses in Office.
    """
    def __init__(self) -> None:
        raise NotImplementedError

    def __getitem__(self, item: str or int):
        """
        Gets sheet from model, either by the str name of the sheet,
        or the int index.
        :param item: str or int
        :return: Office.Sheet
        """
        raise NotImplementedError
        # implemented by office program specific subclasses

    def sheet_exists(self, sheet_name: str) -> bool:
        raise NotImplementedError
        # implemented by office program specific subclasses

    @property
    def sheets(self):
        raise NotImplementedError
        # implemented by office program specific subclasses


class Sheet:
    i7e_sheet = None  # interface sheet obj. ie; com.sun.star...Sheet
    _reference_row_index = 0
    _reference_column_index = 0

    def __init__(self) -> None:
        raise NotImplementedError

    def get_column(
            self,
            column_identifier: int or float or str
    ):
        """
        Gets column by name if identifier is str, otherwise,
        attempts to get column by index.
        :param column_identifier: int, float, or str
        :return: Office.Column
        """
        if isinstance(column_identifier, str):
            return self.get_column_by_name(column_identifier)
        else:
            return self.get_column_by_index(column_identifier)

    def get_column_by_index(self, column_index: int):
        raise NotImplementedError
        # implemented by office program specific subclasses

    def get_column_by_name(self, column_name: int or float or str):
        """
        Gets column from a passed reference value which is compared
        to each cell value in the reference row.
        This function will return the first column whose name matches
        the passed value.
        :return: Office.Column
        """
        x = self.get_column_index_from_name(column_name)
        return self.get_column_by_index(x) if x is not None else None

    def get_column_index_from_name(
        self,
        column_name: int or float or str
    ) -> int or None:
        """
        Gets column index from name
        :param column_name: int, float, or str
        :return: int or None
        """
        for x, cell in enumerate(self.reference_row):
            if cell.value == column_name:
                return x

    def get_row(self, row_identifier: int or float or str):
        """
        Gets row by name if identifier is str, otherwise by index
        :param row_identifier: int, float, or str
        :return: Office.Row
        """
        if isinstance(row_identifier, str):
            return self.get_row_by_name(row_identifier)
        else:
            return self.get_row_by_index(row_identifier)

    def get_row_by_index(self, row_index: int or str):
        raise NotImplementedError
        # implemented by office program specific subclasses

    def get_row_by_name(self, row_name: int or str or float):
        """
        Gets row from a passed reference value which is compared
        to each cell value in the reference row.
        This function will return the first row whose name matches
        the passed value.
        :return: Office.Column
        """
        y = self.get_row_index_from_name(row_name)
        return self.get_row_by_index(y) if y is not None else None

    def get_row_index_from_name(
            self,
            row_name: int or float or str
    ) -> int or None:
        """
        Gets index of a row from passed name
        :param row_name: int, float, or str
        :return: int or None
        """
        for y, cell in enumerate(self.rows):
            if cell.value == row_name:
                return y

    def get_cell(self, cell_identifier, **kwargs):
        # if cell_identifier is list or tuple, get cell via
        # x, y coordinates
        if isinstance(cell_identifier, (list, tuple)):
            x_identifier = cell_identifier[0]
            y_identifier = cell_identifier[1]
            x_identifier_type = kwargs.get('x_identifier_type', None)
            y_identifier_type = kwargs.get('y_identifier_type', None)
            # sanity check
            assert x_identifier_type in ('index', 'name', None), \
                "x identifier type should be 'index', 'name', or None." \
                "Instead got %s" % x_identifier_type
            assert y_identifier_type in ('index', 'name', None), \
                "y identifier type should be 'index', 'name', or None." \
                'instead got %s' % y_identifier_type
            if (x_identifier_type == 'name' or
                x_identifier_type is None and isinstance(
                    x_identifier, str)):
                column = self.get_column_by_name(x_identifier)
            else:
                assert isinstance(x_identifier, int)  # sanity check
                column = self.get_column_by_index(x_identifier)
            if (y_identifier_type == 'name' or
                x_identifier_type is None and isinstance(
                    y_identifier, str)):
                return column.get_cell_by_reference(y_identifier)
            else:
                return column.get_cell_by_index(y_identifier)

    @property
    def reference_row_index(self) -> int:
        """
        Gets index of reference row
        :return: int
        """
        return self._reference_row_index

    @reference_row_index.setter
    def reference_row_index(self, new_index: int) -> None:
        """
        Sets reference row by passing the index of the new row.
        Must be > 0
        :param new_index: int
        :return: None
        """
        if new_index < 0:
            raise IndexError('Reference row index must be > 0')
        self._reference_row_index = new_index

    @property
    def reference_row(self):
        """
        Gets reference row
        :return: Office.Row
        """
        return self.get_row(self.reference_row_index)

    @property
    def reference_column_index(self) -> int:
        """
        Gets index of reference column
        :return: int
        """
        return self._reference_column_index

    @reference_column_index.setter
    def reference_column_index(self, new_index) -> None:
        """
        Sets reference column by passing the index of the new
        reference column.
        Must be > 0.
        :param new_index: int
        :return: None
        """
        if new_index < 0:
            raise IndexError('Reference row index must be > 0')
        self._reference_column_index = new_index

    @property
    def reference_column(self):
        """
        Gets reference column
        :return: Office.Column
        """
        return self.get_column(self.reference_column_index)

    @property
    def columns(self):
        return LineSeries(reference_line=self.reference_row)

    @property
    def rows(self):
        return LineSeries(reference_line=self.reference_column)


class LineSeries:
    """Class storing collection of Line, Column, or Row objects"""

    def __init__(self, reference_line) -> None:
        self.reference_line = reference_line

    def __getitem__(self, item: int or float or str):
        """
        If item is int, returns line of that index, otherwise looks
        for a line of that name.
        :param item: int, float, or str
        :return: Line or None
        """
        if isinstance(item, int):
            return self.get_by_index(item)
        else:
            return self.get_by_name(item)

    def __iter__(self):
        for cell in self.reference_line:
            if self._contents_type == 'rows':
                yield cell.row
            elif self._contents_type == 'columns':
                yield cell.column

    def get_by_name(self, name: int or float or str):
        """
        Gets line from passed line name.
        Returns None if no line of that name is found.
        :param name: int, float or str
        :return: Line or None
        """
        for cell in self.reference_line:
            if cell.value == name:
                if self._contents_type == 'columns':
                    return cell.column
                elif self._contents_type == 'rows':
                    return cell.row

    def get_by_index(self, index: int):
        """
        Gets line from passed line index
        :param index:
        :return: Line
        """
        if self._contents_type == 'rows':
            return self.sheet.get_row_by_index(index)
        elif self._contents_type == 'columns':
            return self.sheet.get_column_by_index(index)

    @property
    def sheet(self) -> Sheet:
        """
        Gets sheet that owns the Columns or Rows of this Lines obj.
        :return: Sheet
        """
        return self.reference_line.sheet

    @property
    def names(self):
        """
        Yields names of lines in LineList
        :return: int, float, or str
        """
        for line in self:
            yield line.name

    @property
    def indexes(self):
        """
        Yields indexes of lines in LineList
        :return: int
        """
        for line in self:
            yield line.index

    @property
    def _contents_type(self) -> str:
        if isinstance(self.reference_line, Row):
            return 'columns'
        elif isinstance(self.reference_line, Column):
            return 'rows'


class Line:
    sheet = None  # these are all to be set on init in subclasses
    index = None  # index of this line.

    def __getitem__(self, item: int or str):
        raise NotImplementedError
        # implemented by office program specific subclasses

    def __iter__(self):
        raise NotImplementedError
        # implemented by office program specific subclasses

    def __len__(self):
        raise NotImplementedError
        # implemented by office program specific subclasses

    def get_cell_by_index(self, index: int):
        raise NotImplementedError
        # implemented by Row and Column in office program
        # specific subclasses

    def get_cell_by_reference(self, reference: str or float or int):
        for i, cell in enumerate(self._reference_line):
            if cell.value == reference:
                return self.get_cell_by_index(i)

    def clear(self, include_header: bool = False):
        """
        Clears line of cells.
        If Include header is True; clears cell data in cells
        preceding and including re
        a
        :param include_header: bool
        :return: None
        """
        [cell.clear() for i, cell in enumerate(self)
         if i > self.name_cell_index or include_header]

    @property
    def _reference_line(self):
        raise NotImplementedError

    @property
    def duplicates(self):
        """
        Returns generator of duplicate cells in Column.
        :return: cells (iterator)
        """
        cell_values = set()
        for cell in self:
            if cell.value_without_whitespace in cell_values:
                yield cell
            cell_values.add(cell.value_without_whitespace)

    @property
    def name_cell_index(self) -> int:
        """
        Gets the index of the cell which contains this line's name.
        :return: int
        """
        raise NotImplementedError

    @property
    def name(self):
        """
        Returns name of line, which is the value stored in the
        line's header cell, located in the sheet's reference
        row or column.
        :return: int, float, str or None
        """
        return self[self.name_cell_index].value


class Column(Line):
    """
    # this class exists for typing purposes, to provide a
    # common parent for Rows
    """

    @property
    def _reference_line(self):
        return self.reference_column

    @property
    def reference_column(self):
        return self.sheet.reference_column

    @property
    def name_cell_index(self) -> int:
        """
        Gets the index of the cell which contains this
        Column's name.
        :return: int
        """
        return self.sheet.reference_row_index


class Row(Line):
    """
    # this class exists for typing purposes, to provide a
    # common parent for Rows
    """

    @property
    def _reference_line(self):
        return self.reference_row

    @property
    def reference_row(self):
        """
        Gets reference row.
        This is the row that contains the names of the
        intersecting columns, allowing fetching of cells in
        this row via passage of a reference string
        :return: Row
        """
        return self.sheet.reference_row

    @property
    def name_cell_index(self) -> int:
        """
        Gets the index of the cell which contains this Row's name.
        :return: int
        """
        return self.sheet.reference_column_index


class Cell:
    position = None
    sheet = None

    def __init__(self):
        raise NotImplementedError

    def set_color(self, color: int or list or tuple) -> None:
        raise NotImplementedError

    def remove_whitespace(self):
        raise NotImplementedError

    def clear(self):
        """Clears cell by setting value to None and color to default"""
        self.value = None
        self.set_color(DEFAULT_COLOR)

    @property
    def row(self) -> Row:
        return self.sheet.get_row(self.y)

    @property
    def column(self) -> Column:
        return self.sheet.get_column(self.x)

    @property
    def has_whitespace(self) -> bool:
        raise NotImplementedError

    @property
    def value_without_whitespace(self):
        raise NotImplementedError

    @property
    def value(self) -> int or float or str or None:
        raise NotImplementedError

    @value.setter
    def value(self, new_value: str or int or float or None) -> None:
        raise NotImplementedError

    @property
    def string(self):
        raise NotImplementedError

    @string.setter
    def string(self, new_string: str) -> None:
        raise NotImplementedError

    @property
    def float(self):
        raise NotImplementedError

    @float.setter
    def float(self, new_float: int or float) -> None:
        raise NotImplementedError

    @property
    def x(self):
        raise NotImplementedError

    @property
    def y(self):
        return NotImplementedError


class Interface:
    """Abstract class inherited from by XW and Uno interfaces."""

    class Model:
        pass

    class Sheet:
        pass

    class Line:
        pass

    class Column:
        pass

    class Row:
        pass

    class Cell:
        pass


class Office:
    """
    Handles interface with workbook.

    This may not need to be a class, but any independent functions appear
    as their own macro, so this is instead its own class
    """

    class XW(Interface):
        """
        Handles XLWings interfacing with Office program
        """

        class Model(Model):
            def __init__(self):
                pass

    class Uno(Interface):
        """
        Handles Uno interfacing with Office program
        """

        class Model(Model):
            """
            Handles usages of PyUno Model
            """

            def __init__(self) -> None:
                # not an error; provided by macro caller
                desktop = XSCRIPTCONTEXT.getDesktop()
                py_uno_model = desktop.getCurrentComponent()
                if not hasattr(py_uno_model, 'Sheets'):
                    raise AttributeError(
                        'Model does not have Sheets. '
                        'This macro needs to be run from a calc workbook.'
                    )
                self.model = py_uno_model

            def __getitem__(self, item: str or int) -> Sheet:
                """
                Gets identified sheet.
                :param item: str or int
                :return: Sheet
                """
                assert isinstance(item, (str, int))
                # try to get appropriate sheet from uno model.
                # If sheet index or name cannot be found, raise a more
                # readable error message than the terribly unhelpful
                # uno message.
                if isinstance(item, int):
                    try:
                        return Office.Uno.Sheet(
                            self.model.Sheets.getByIndex(item))
                    except:  # can't seem to put the actual exception
                        # class here
                        raise IndexError('Could not retrieve sheet at index'
                                         '%s' % repr(item))
                else:
                    try:
                        return Office.Uno.Sheet(
                            self.model.Sheets.getByName(item))
                    except:
                        raise KeyError('Could not retrieve sheet with name %s'
                                       % repr(item))

            def sheet_exists(self, *args: str) -> str:
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

            @property
            def sheets(self):
                """
                Generator returning each sheet in Model / Book
                :return: Sheet
                """
                i = 0
                while True:  # loop until break
                    try:
                        yield Office.Uno.Sheet(self.model.Sheets.getByIndex(i))
                    except:
                        break
                    else:
                        i += 1

        class Sheet(Sheet):
            """
            Handles usage of a workbook sheet
            """

            def __init__(
                    self,
                    uno_sheet,
                    reference_row_index=0,
                    reference_column_index=0
            ) -> None:
                self.i7e_sheet = uno_sheet
                self.reference_row_index = reference_row_index
                self.reference_column_index = reference_column_index

            def get_column(self, column_identifier: int or str) -> Column:
                """
                Gets column from name
                :param column_identifier: str or int
                identifying the column to retrieve
                :return: Column
                """
                assert isinstance(column_identifier, (int, str)), \
                    'getitem must be passed an int or str, got %s' \
                    % column_identifier
                if isinstance(column_identifier, int):
                    column_index = column_identifier
                else:
                    column_index = self.get_column_index_from_name(
                        column_identifier)
                return self.get_column_by_index(column_index) if \
                    column_index is not None else None

            def get_row(self, row_identifier: str or int) -> Row:
                """
                Gets row from identifier
                :param row_identifier:
                :return:
                """
                assert isinstance(row_identifier, (int, str)), \
                    'getitem must be passed an int or str, got %s' \
                    % row_identifier
                if isinstance(row_identifier, int):
                    row_index = row_identifier
                else:
                    row_index = self.get_row_index_from_name(row_identifier)
                return self.get_row_by_index(row_index) if \
                    row_identifier is not None else None

            def get_column_by_index(self, column_index: int) -> Column:
                """
                Gets column of passed index
                :param column_index: int
                :return: Column
                """
                if not isinstance(column_index, int):
                    raise TypeError('Column index must be an int, got %s'
                                    % column_index)
                return Office.Uno.Column(
                    sheet=self,
                    column_index=column_index,
                    reference_column_index=self.reference_column_index
                )

            def get_row_by_index(self, row_index: int or str) -> Row:
                """
                Gets row of passed index
                :param row_index: int
                :return: Row
                """
                if not isinstance(row_index, int):
                    raise TypeError('row_index must be an int, got %s '
                                    % row_index)
                return Office.Uno.Row(
                    sheet=self,
                    row_index=row_index,
                    reference_row_index=self.reference_row_index
                )

            @property
            def columns(self):
                """
                yields columns in sheet
                :return: Columns
                """
                for x, cell, in enumerate(self.reference_row):
                    yield self.get_column(x)

            @property
            def rows(self):
                """
                yields rows in sheet
                :return: Rows
                """
                for y, cell in enumerate(self.reference_column):
                    yield self.get_column(y)

        class Line(Line):
            """
            Contains methods common to both Columns and Rows
            """
            def __init__(
                self,
                sheet: Sheet,
                index: int,
                reference_index: int,
            ) -> None:
                if not isinstance(sheet, Sheet):
                    raise TypeError(
                        'Expected subclass of Sheet. Instead got %s'
                        % repr(sheet))
                if not isinstance(index, int):
                    raise TypeError(
                        'Expected line index to be an int. '
                        'Instead got %s' % repr(index))
                if not isinstance(reference_index, int):
                    raise TypeError(
                        'Expected reference name index to be an int, '
                        'Instead got %s' % repr(reference_index))
                self.sheet = sheet
                self.index = index
                self.reference_index = index

            def __len__(self) -> int:
                n = 0
                for each in self:
                    n += 1
                return n

            @property
            def uno_sheet(self):
                """
                Gets uno sheet object
                :return: uno sheet
                """
                return self.sheet.i7e_sheet

        class Column(Line, Column):
            """
            Handles usage of a column within a sheet
            """
            def __init__(
                    self,
                    sheet: Sheet,
                    column_index: int,
                    reference_column_index: int=0):
                super().__init__(
                    sheet=sheet,
                    index=column_index,
                    reference_index=reference_column_index
                )

            def __getitem__(self, cell_identifier) -> Cell:
                """
                Gets cell from passed identifier.
                If identifier is string, presumes it is a cell's name.
                If identifier is number, presumes it is a
                cell's index.
                To ensure the right method of fetching a cell is used,
                use .get_by_name or .get_by_index
                :param cell_identifier: str or int
                :return: Cell
                """
                assert isinstance(cell_identifier, (int, str)), \
                    'Expected cell_identifier to be int or str, got %s ' \
                    % cell_identifier
                if isinstance(cell_identifier, int):
                    return self.get_cell_by_index(cell_identifier)
                else:
                    for x, cell in enumerate(self.reference_column):
                        if cell.value == cell_identifier:
                            return self[x]

            def __iter__(self):
                """
                Returns iterable line of cells
                :return: Iterable
                """
                return Office.Uno.CellLine(
                    sheet=self.sheet,
                    axis='y',
                    index=self.index)

            def get_cell_by_index(self, index: int) -> Cell:
                """
                Gets cell from passed index.
                :param index: int
                :return: Cell
                """
                if not isinstance(index, int):
                    raise TypeError("Passed index must be an int, got %s"
                                    % index)
                return Office.Uno.Cell(
                    self.sheet, (self.index, index))

        class Row(Line, Row):
            """
            Handles usage of a row within a sheet
            """

            def __init__(
                    self,
                    sheet: Sheet,
                    row_index: int,
                    reference_row_index: int=0
            ) -> None:
                super().__init__(
                    sheet=sheet,
                    index=row_index,
                    reference_index=reference_row_index,
                )

            def __getitem__(self, cell_identifier) -> Cell:
                """
                Gets cell from passed identifier.
                If identifier is string, presumes it is a cell's name.
                If identifier is number, presumes it is a
                cell's index.
                To ensure the right method of fetching a cell is used,
                use .get_by_name or .get_by_index.
                :param cell_identifier: str or int
                :return: Cell
                """
                assert isinstance(cell_identifier, (str, int))
                if isinstance(cell_identifier, int):
                    return self.get_cell_by_index(cell_identifier)
                else:
                    for x, cell in enumerate(self.reference_row):
                        if cell.value == cell_identifier:
                            return self[x]

            def __iter__(self):
                return Office.Uno.CellLine(
                    sheet=self.sheet,
                    axis='x',
                    index=self.index)

            def get_cell_by_index(self, index: int) -> Cell:
                """
                Gets cell in Row from passed index
                :param index: int
                :return: Cell
                """
                if not isinstance(index, int):
                    raise TypeError('Passed index should be int, got %s'
                                    % index)
                return Office.Uno.Cell(
                    sheet=self.sheet,
                    position=(index, self.index))

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

            def __next__(self) -> Cell:
                x, y = (self.index, self.i) if self.axis == 'y' else \
                    (self.i, self.index)
                cell = Office.Uno.Cell(self.sheet, (x, y))
                if cell.string == '' and self.i > self.highest_inhabited_i:
                    for x in range(1, MAX_CELL_GAP):
                        test_x, test_y = (self.index, self.i + x) if \
                            self.axis == 'y' else (self.i + x, self.index)
                        test_cell = Office.Uno.Cell(
                            self.sheet,
                            position=(test_x, test_y))
                        if test_cell.string != '':
                            self.highest_inhabited_i = self.i + x
                            break
                    else:
                        raise StopIteration()
                self.i += 1
                return cell

        class Cell(Cell):
            """
            Handles usage of an individual cell
            """

            def __init__(
                    self,
                    sheet: Sheet,
                    position: tuple
            ) -> None:
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
                    color_int = color[0] * 256 ** 2 + color[1] * 256 + color[2]
                self._source_cell.CellBackColor = color_int

            def remove_whitespace(self) -> None:
                """Removes whitespace from cell"""
                self.value = self.value_without_whitespace

            @property
            def _uno_sheet(self):
                """
                Gets uno Sheet obj.
                :return: uno Sheet obj
                """
                return self.sheet.i7e_sheet

            @property
            def value_without_whitespace(self) -> str:
                """
                Gets value of cell without whitespace.
                If cell is not a string, returns value unchanged.
                :return:
                """
                if isinstance(self.value, str):
                    return self.value.strip()
                else:
                    return self.value

            @property
            def has_whitespace(self) -> bool:
                """
                Gets bool of whether cell string contains whitespace.
                If cell contains a number, returns False.
                :return: bool
                """
                return self.value_without_whitespace != self.value

            @property
            def _source_cell(self):
                """
                Gets PyUno cell from which values are drawn
                :return:
                """
                return self._uno_sheet.getCellByPosition(*self.position)

            @property
            def value(self) -> int or float or str:
                """
                Gets value of cell.
                :return: str or float
                """
                # get cell value type after formula evaluation has been
                # carried out. This will return the cell value's type
                # even if it is not a formula
                t = self._source_cell.FormulaResultType.value
                if t == 'TEXT':
                    return self._source_cell.getString()
                elif t == 'VALUE':
                    return self._source_cell.getValue()

            @value.setter
            def value(self, new_value: int or float or str) -> None:
                """
                Sets source cell string and number value appropriately for
                a new value.
                This does not handle formulas at the present time.
                :param new_value: int, float, or str
                """
                assert isinstance(new_value, (str, int, float))
                if isinstance(new_value, str):
                    self.string = new_value
                else:
                    self.float = new_value

            @property
            def string(self) -> str:
                """
                Returns string value directly from source cell
                :return: str
                """
                return self._source_cell.getString()

            @string.setter
            def string(self, new_string: str) -> None:
                """
                Sets string value of source cell directly
                :param new_string: str
                """
                assert isinstance(new_string, str)
                self._source_cell.setString(new_string)

            @property
            def float(self) -> float:
                """
                Returns float value directly from source cell 'value'
                :return: float
                """
                return self._source_cell.getValue()

            @float.setter
            def float(self, new_float: int or float) -> None:
                """
                Sets float value of source cell directly
                :param new_float: int or float
                :return: None
                """
                assert isinstance(new_float, (int, float))
                new_value = float(new_float)
                self._source_cell.setValue(new_value)

            @property
            def x(self) -> int:
                """
                Gets x position of cell
                :return: int
                """
                return self.position[0]

            @property
            def y(self) -> int:
                """
                Gets y position of cell
                :return: int
                """
                return self.position[1]

            def __str__(self) -> str:
                return 'Cell[(%s), Value: %s' % (self.position, self.value)

    @staticmethod
    def get_interface() -> str or None:
        """
        Test for what interface is using this macro, and return the string
        of the appropriate class that should be used.
        :return: str or None if no interface can be determined
        """
        # test for Python Uno
        try:
            XSCRIPTCONTEXT  # if this variable exists, PyUno is being used.
        except AttributeError:
            pass
        else:
            return 'Uno'

            # test for XLWings
            # todo

            # otherwise, return None / False

    @staticmethod
    def get_interface_class() -> Interface:
        """Gets interface class, ie, Uno or XW"""
        interface = Office.get_interface()  # gets str name of interface class
        if not interface:
            raise ValueError('Should be run as macro using XLWings or PyUno.'
                             'Neither could be detected.')
        return getattr(Office, interface)

    @staticmethod
    def get_model() -> Model:
        return Office.get_model_class()()  # get model class and instantiate

    @staticmethod
    def get_model_class() -> type:
        """Gets appropriate Model class"""
        return Office.get_interface_class().Model

    @staticmethod
    def get_sheet_class() -> type:
        """Gets appropriate Sheet class"""
        return Office.get_interface_class().Sheet

    @staticmethod
    def get_column_class() -> type:
        """Gets appropriate Column class"""
        return Office.get_interface_class().Column

    @staticmethod
    def get_row_class() -> type:
        """Gets appropriate Row class"""
        return Office.get_interface_class().Row

    @staticmethod
    def get_cell_class() -> type:
        """Gets appropriate Cell class"""
        return Office.get_interface_class().Cell

###############################################################################
# Column Data


class Translation:
    """
    Handles movement of data from source to target sheets and applies
    modifications
    """
    _whitespace_action = WHITESPACE_HIGHLIGHT_STR
    _duplicate_action = DUPLICATE_HIGHLIGHT_STR

    def __init__(
            self,
            dialog_parent,
            source_sheet: Sheet,
            target_sheet: Sheet,
            column_translations=None,
            row_deletions=None,
            source_start_row=1,
            target_start_row=1,
            whitespace_action=WHITESPACE_HIGHLIGHT_STR,
            duplicate_action=DUPLICATE_HIGHLIGHT_STR,
    ):

        if not isinstance(source_sheet, Sheet):
            raise TypeError('Source sheet should be a Sheet, got: %s'
                            % repr(source_sheet))
        if not isinstance(target_sheet, Sheet):
            raise TypeError('Target sheet should be a Sheet, got: %s'
                            % repr(source_sheet))
        self._dialog_parent = dialog_parent
        self._source_sheet = source_sheet
        self._target_sheet = target_sheet
        self._row_deletions = row_deletions if row_deletions else set()
        self._src_cell_transforms = {}
        self._tgt_cell_transforms = {}
        self._source_start_row = source_start_row
        self._target_start_row = target_start_row
        self._whitespace_action = whitespace_action
        self._duplicate_action = duplicate_action
        # create column translations from passed list of dicts
        # in settings
        self._column_translations = []
        self.add_column_translation(*column_translations)

    def confirm_overwrite(self):
        reply = QtW.QMessageBox.question(
            self._dialog_parent,
            'Overwrite Cells?',
            'Cells on the target sheet will be overwritten.\n'
            'Proceed?',
            QtW.QMessageBox.Yes | QtW.QMessageBox.Cancel,
            QtW.QMessageBox.Cancel
        )
        return reply == QtW.QMessageBox.Yes

    def add_column_translation(self, *args, **kwargs) -> None:
        """
        Adds translation to queue which when applied, copies cell data
        from source column to target column.
        source and target columns may be identified either by passing
        the name of that column, as determined by the sheet's reference
        row, or by their index.
        An index or name must be passed for both source and target
        columns, however passing both an index and a name will result
        in a ValueError being raised.
        If passed kwargs, will pass on those to a
        created ColumnTranslation obj.
        If passed a dictionary or dictionaries, will add one
        ColumnTranslation for each of those dictionaries, and pass it
        the contained kwargs.
            source_column_i: int
            source_column_name: int, float, or str
            target_column_i: int
            target_column_name: int, float, or str
            kwargs: other kwargs will be passed to created
        ColumnTranslation.
        :param args: ColumnTranslation kwargs dictionaries
        :param kwargs: kwargs for a single ColumnTranslation.
        """
        # check that passed args are all dictionaries
        assert all([isinstance(item, dict) for item in args]), \
            'passed args must be dictionaries of kwargs for ' \
            'ColumnTranslation. Instead got %s' % args
        # for each passed kwargs dictionary,
        # including that passed to this method;
        for kwargs_dict in args + (kwargs,) if kwargs else args:
            # ensure correct kwargs were passed.
            # Exactly one source column identifier should have been
            # passed for each of src col and tgt col
            source_column_i = kwargs_dict.get(SOURCE_COLUMN_INDEX_KEY, None)
            source_column_name = kwargs_dict.get(SOURCE_COLUMN_NAME_KEY, None)
            target_column_i = kwargs_dict.get(TARGET_COLUMN_INDEX_KEY, None)
            target_column_name = kwargs_dict.get(TARGET_COLUMN_NAME_KEY, None)
            if bool(source_column_i) == bool(source_column_name):
                raise ValueError(
                    'One of source_column_i or source_column_name must '
                    'be passed, but not both. Got %s and %s respectively'
                    % (source_column_i, source_column_name)
                )
            if bool(target_column_i) == bool(target_column_name):
                raise ValueError(
                    'One of target_column_i or target_column_name must '
                    'be passed, but not both. Got %s and %s respectively'
                    % (target_column_i, target_column_name)
                )
            # add ColumnTranslation
            self._column_translations.append(
                ColumnTranslation(
                    parent_translation=self,
                    **kwargs_dict
                )
            )

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
        # add cell transformations to be applied after move
        self._add_cell_transformations()
        # clear data
        self.clear_target()
        # move data
        # for each column translation
        for column_translation in self._column_translations:
            column_translation.commit()
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
                    if self.confirm_overwrite:
                        print('confirm dlg')
                        proceed = self.confirm_overwrite()
                        if not proceed:
                            return False
                    user_ok = True
                cell.value = ''
                cell.set_color(DEFAULT_COLOR)

    def _add_cell_transformations(self):
        """
        Goes through columns and looks for whitespace / duplicates.
        Applies cell transformations (removal / highlight) as needed.
        """
        for column_translation in self._column_translations:
            source_column = self._source_sheet.get_column(
                column_translation.source_column_i
            )
            # duplicates
            self._add_whitespace_cell_transformations(source_column)
            # whitespace
            self._add_duplicate_cell_transformations(source_column)

    def _add_whitespace_cell_transformations(self, source_column):
        """
        checks for whitespace in cells of source_column and takes
        set action (remove, highlight, ignore).
        Written to be called by _add_cell_transformations method.
        :param source_column: Column
        """
        # find whitespace cells
        whitespace_cells = [
            cell for cell in source_column if
            cell.value_without_whitespace != cell.value
            ]
        # add cell transformations
        [self._add_whitespace_cell_transformation(cell)
         for cell in whitespace_cells]
        # give user message about whitespace action
        if whitespace_cells:
            # get positions of whitespace
            whitespace_positions = [
                cell.position for cell in whitespace_cells
                ]
            self._whitespace_feedback(whitespace_positions)

    def _whitespace_feedback(self, whitespace_positions):
        """
        Reports to user on whitespace removals.
        Written to be called by _add_whitespace_cell_transforms method
        after whitespace transforms have been added.
        :param whitespace_positions:
        """
        if not whitespace_positions:
            return
        secondary_string = ''
        if self.whitespace_action == WHITESPACE_REMOVE_STR:
            secondary_string = (
                'Cell values were edited to remove '
                'unneeded '
                'tab, linefeed, return, formfeed, '
                'and/or vertical tab characters.')
        elif self.whitespace_action == WHITESPACE_HIGHLIGHT_STR:
            secondary_string = (
                '%s Cell values were highlighted in '
                'checked '
                'columns' % len(whitespace_positions))
        InfoMessage(
            parent=self,
            title='Whitespace Found',
            main='Whitespace found in %s cells' % len(
                whitespace_positions),
            secondary=secondary_string,
            detail=self._position_report(*whitespace_positions)
        )

    def _add_whitespace_cell_transformation(self, cell):
        """
        Adds cell transformation for a cell containing whitespace.
        Action taken depends on whitespace action setting.
        Cell and row may be highlighted, whitespace removed, or the
        cell ignored.
        :param cell: cell containing whitespace.
        """
        assert cell.value_without_whitespace != cell.value
        if self.whitespace_action == WHITESPACE_HIGHLIGHT_STR:
            # color cell row when it is moved.
            self._color_row(
                cell_position=cell.position,
                cell_color=WHITESPACE_CELL_COLOR,
                row_color=WHITESPACE_ROW_COLOR
            )
        elif self.whitespace_action == WHITESPACE_REMOVE_STR:
            # run remove whitespace function on cell when it is moved
            self.add_cell_transform(
                cell.position,
                'src',
                lambda c: c.remove_whitespace()
            )

    def _add_duplicate_cell_transformations(self, source_column):
        [self._add_duplicate_cell_transformation(cell)
         for cell in source_column.duplicates]
        if source_column.duplicates:
            duplicate_positions = [
                cell.position for cell in source_column.duplicates
                ]
            self._duplicates_feedback(duplicate_positions)

    def _add_duplicate_cell_transformation(self, cell):
        """
        Adds cell transformation for a cell with a duplicate value.
        Action depends on duplicate cell action setting;
        Row may be removed, highlighted, or ignored.
        :param cell: cell containing duplicate value.
        """
        if self.duplicate_action == DUPLICATE_HIGHLIGHT_STR:
            self._color_row(
                cell_position=cell.position,
                cell_color=DUPLICATE_CELL_COLOR,
                row_color=DUPLICATE_ROW_COLOR
            )
        elif self.duplicate_action == DUPLICATE_REMOVE_ROW_STR:
            self.add_row_deletion(cell.y)

    def _duplicates_feedback(
            self,
            duplicate_positions) -> None:
        """
        Provides feedback to user about duplicates and actions taken
        regarding said duplicates.
        :param duplicate_positions: iterable of duplicate_positions
        """
        if not duplicate_positions or \
                self.duplicate_action == DUPLICATE_IGNORE_STR:
            return
        secondary_string = ''
        if self.duplicate_action == DUPLICATE_HIGHLIGHT_STR:
            secondary_string = '%s Cell values were highlighted in ' \
                               'checked columns' % duplicate_positions
        elif self.duplicate_action == DUPLICATE_REMOVE_ROW_STR:
            n_rows_w_duplicates = len(set(
                [pos[1] for pos in duplicate_positions]))
            secondary_string = '%s Cell rows containing duplicate ' \
                               'values were removed' % n_rows_w_duplicates,
        InfoMessage(
            parent=self,
            title='Duplicate Values',
            main='%s Duplicate cell values found' % duplicate_positions,
            secondary=secondary_string,
            detail=self._position_report(*duplicate_positions)
        )

    def _color_row(self, cell_position, cell_color, row_color):
        """
        Colors a cell and row background.
        :param cell_position: position of cell.
        :param cell_color: color for cell to be colored.
        :param row_color: color for all other cells in row to be colored.
        """
        [self.add_cell_transform(
            (x, cell_position[1]),
            'src',
            lambda c: c.set_color(row_color)
        ) for x in range(len(
            self._source_sheet.get_row(cell_position[1])))]
        # mark cell with duplicate red1
        self.clear_cell_transform(
            cell_position, 'src')
        self.add_cell_transform(
            cell_position, 'src',
            lambda c: c.set_color(cell_color))

    def _position_report(self, *src_positions):
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
                        self._column_translations:
                    assert isinstance(col_transform,
                                      ColumnTranslation)
                    if col_transform.source_column_i == x_:
                        return col_transform

            # find column the x index will be moved to
            # by looking through column transforms
            x_translation = find_col_translation(
                src_pos_[0])
            assert isinstance(x_translation, ColumnTranslation)
            tgt_x = x_translation.target_column_i
            tgt_y = src_pos_[1] - self.source_start_row + \
                self.target_start_row
            return tgt_x, tgt_y

        # first convert src positions to tgt positions
        tgt_positions = [src_to_tgt_pos(src_pos_)
                         for src_pos_ in src_positions]

        rows = []  # list of row indices in report.
        # This keeps the columns in order.
        row_columns = {}  # dictionary of string lists
        for x, y in tgt_positions:
            column_name = self._target_sheet.get_column(x).name
            if y not in rows:
                row_columns[y] = list()
                rows.append(y)
            row_columns[y].append(column_name)
        # now make the report
        row_strings = [
            'Row %s; %s' % (y, ', '.join(row_columns[y]))
            for y in rows]
        return '\n'.join(row_strings)

    @property
    def source_sheet(self):
        """
        Gets source sheet
        :return: Sheet
        """
        return self._source_sheet

    @property
    def target_sheet(self):
        """
        Gets target sheet
        :return: Sheet
        """
        return self._target_sheet

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

    @property
    def row_deletions(self) -> set:
        """
        Gets set of rows to be deleted in translation
        :return: set
        """
        return self._row_deletions.copy()

    @property
    def whitespace_action(self):
        """
        Gets name of action that will be taken for cells containing
        whitespace
        :return: str
        """
        return self._whitespace_action

    @whitespace_action.setter
    def whitespace_action(self, action):
        """
        Sets action to be taken when cell contains whitespace
        :param action: str
        """
        assert action in (
            WHITESPACE_REMOVE_STR,
            WHITESPACE_HIGHLIGHT_STR,
            WHITESPACE_IGNORE_STR
        )
        self._whitespace_action = action

    @property
    def duplicate_action(self):
        """
        Gets name of action that will be taken for rows containing
        duplicates
        :return: str
        """
        return self._duplicate_action

    @duplicate_action.setter
    def duplicate_action(self, action):
        """
        Sets name of action that will be taken for rows
        containing duplicates
        :param action: str
        """
        assert action in (
            DUPLICATE_REMOVE_ROW_STR,
            DUPLICATE_HIGHLIGHT_STR,
            DUPLICATE_IGNORE_STR
        )
        self._duplicate_action = action

    @property
    def src_cell_transforms(self):
        """
        Gets cell transforms that are to be applied based on src
        sheet position.
        :return: dict{src_sheet_position: list[function]}
        """
        return self._src_cell_transforms.copy()

    @property
    def tgt_cell_transforms(self):
        """
        Gets cell transforms that are to be applied based on tgt
        sheet position
        :return: dict{tgt_sheet_position: list[function]}
        """
        return self._tgt_cell_transforms.copy()


class ColumnTranslation:
    """
    Handles movement and modification of a column
    Applies translation of individual column
    """

    def __init__(
            self,
            parent_translation: Translation,
            source_column_i=None,
            target_column_i=None,
            source_column_name=None,
            target_column_name=None,
            check_for_whitespace: bool=True,
            check_for_duplicates: bool=False) -> None:
        if (
            bool(source_column_i is None) ==
            bool(source_column_name is None),
        ) is True:  # no idea why, but without 'is True' this will always
            # raise the ValueError
            raise ValueError(
                'Source column index or name must be passed, but not both. '
                'Got args source_column_i: %s (%s) and source_column_name: %s'
                ' (%s) respectively'
                % (source_column_i, source_column_i.__class__.__name__,
                   source_column_name, source_column_name.__class__.__name__))
        if (
            bool(target_column_i is None) ==
            bool(target_column_name is None),
        ) is True:  # no idea why, but without 'is True' this will always
            # raise the ValueError
            raise ValueError(
                'Target column index or name must be passed, but not both. '
                'Got args target_column_i: %s (%s) and target_column_name: %s'
                '(%s)'
                % (target_column_i, target_column_i.__class__.__name__,
                   target_column_name, target_column_name.__class__.__name__)
            )
        self._parent_translation = parent_translation
        self._target_column_i = target_column_i
        self._source_column_i = source_column_i
        self._target_column_name = target_column_name
        self._source_column_name = source_column_name
        self._duplicates_check = check_for_duplicates
        self._whitespace_check = check_for_whitespace

    def commit(self) -> None:
        """
        Applies column translation.
        Moves each cell in source column to target.
        Skips rows that are listed in Translation.row_deletions
        Applies cell transformations
        :return: None
        """
        i = self._parent_translation.target_start_row
        # for each cell in the source sheet column
        for source_cell in self.source_column:
            # don't include source cells before start row
            # and those whose y position is in deletion set.
            if source_cell.y in self._parent_translation.row_deletions or \
                    source_cell.y < self._parent_translation.source_start_row:
                continue
            assert isinstance(source_cell, Cell)
            tgt_x = self.target_column.index
            tgt_y = i + self._parent_translation.target_start_row - \
                self._parent_translation.source_start_row
            assert isinstance(tgt_x, int)
            assert isinstance(tgt_y, int)
            target_cell = self.target_sheet.get_cell((tgt_x, tgt_y))
            assert isinstance(target_cell, Cell)
            target_cell.value = source_cell.value
            # apply cell transforms
            src_cell_transforms = self._parent_translation.src_cell_transforms
            tgt_cell_transforms = self._parent_translation.tgt_cell_transforms
            try:  # try to apply transforms pinned to the src cell position
                [transform(target_cell) for transform in
                 src_cell_transforms[source_cell.position]]
            except KeyError:
                pass  # no transforms for that src cell position
            try:  # try to apply transforms pinned to the tgt cell position
                [transform(target_cell) for transform in
                 tgt_cell_transforms[target_cell.position]]
            except KeyError:
                pass  # no transforms for that tgt cell position
            i += 1

    # source sheet getters / setters

    @property
    def source_sheet(self) -> Sheet:
        """
        Gets source sheet, from which cells are retrieved
        :return: Sheet
        """
        return self._parent_translation.source_sheet

    @property
    def source_column_i(self) -> int:
        """
        Gets source column identifier
        :return: int
        """
        if self._source_column_i is not None:
            return self._source_column_i
        else:
            return self.source_column.index

    @source_column_i.setter
    def source_column_i(self, new_column: int):
        """
        Sets source column
        :param new_column: int
        """
        assert isinstance(new_column, int)
        self._source_column_i = new_column
        self._source_column_name = None

    @property
    def source_column_name(self) -> int or str or float or None:
        """
        Gets name by which the source column is identified.
        If the source column is identified by index, will return None
        :return: int, float, str, or None
        """
        if self._source_column_name is not None:
            return self._source_column_name
        else:
            return self.source_column.name

    @source_column_name.setter
    def source_column_name(self, new_column_name) -> None:
        """
        Sets name by which source column will be identified
        :param new_column_name: int, float or str
        :return: None
        """
        assert isinstance(new_column_name, (int, float, str))
        if new_column_name not in self.source_sheet.columns.names:
            raise ValueError('Passed column name %s not found in source sheet'
                             % new_column_name)
        self._source_column_name = new_column_name
        self._source_column_i = None

    @property
    def source_column(self) -> Column:
        """
        Gets source column
        :return: Office.Column
        """
        if self._source_column_i is not None:
            identifier = self._source_column_i
        else:
            identifier = self._source_column_name
        return self.source_sheet.get_column(identifier)

    # target sheet getters/setters

    @property
    def target_sheet(self):
        """
        Gets target sheet, to which cells are moved
        :return: Sheet
        """
        return self._parent_translation.target_sheet

    @property
    def target_column_i(self) -> int or None:
        """
        Gets target column index, if it is identified by index,
        or else None.
        :return: int or None
        """
        if self._target_column_i is not None:
            return self._target_column_i
        else:
            return self.target_column.index

    @target_column_i.setter
    def target_column_i(self, new_column):
        """
        Sets target column by passing an index by which to identify it.
        :param new_column: int or str
        """
        assert isinstance(new_column, int)
        self._target_column_i = new_column
        self._target_column_name = None

    @property
    def target_column_name(self):
        """
        Gets name by which target column is identified, or else None
        if Column is identified by index.
        :return: int, float, str, or None
        """
        if self._target_column_name is not None:
            return self._target_column_name
        else:
            return self.target_column.name

    @target_column_name.setter
    def target_column_name(self, new_name) -> None:
        """
        Sets name by which target will be identified
        :param new_name: int, float, or str
        :return: None
        """
        assert isinstance(new_name, (int, float, str))
        if new_name not in self.target_sheet.columns.names:
            raise ValueError('Column name %s not found in target sheet'
                             % new_name)
        self._target_column_name = new_name
        self._target_column_i = None

    @property
    def target_column(self) -> Column:
        """
        Gets target column
        :return: Office.Column
        """
        identifier = self._target_column_i if \
            self._target_column_i is not None else \
            self._target_column_name
        return self.target_sheet.get_column(identifier)

    # column translation options

    @property
    def check_for_duplicates(self) -> bool:
        """
        Returns bool of whether column should be checked for duplicates
        :return: bool
        """
        return self._duplicates_check

    @check_for_duplicates.setter
    def check_for_duplicates(self, new_bool: bool):
        """
        Sets bool of whether column should be checked for duplicates
        :param new_bool: bool
        """
        self._duplicates_check = new_bool

    @property
    def check_for_whitespace(self) -> bool:
        """
        Returns bool of whether column should be checked for whitespace
        :return: bool
        """
        return self._whitespace_check

    @check_for_whitespace.setter
    def check_for_whitespace(self, new_bool: bool):
        """
        Gets bool for whether column is checked for whitespace
        :param new_bool: bool
        """
        self._whitespace_check = new_bool

    def get_whitespace_source_cells(self):
        """
        Yields cells in source column which contain whitespace
        :return: iterator of cells
        """
        assert self._parent_translation is not None, \
            "Parent translation must be set"
        for cell in self.source_column:
            if cell.has_whitespace:
                yield cell

    def get_duplicate_source_cells(self):
        """
        Yields cells in source column with values that are duplicates of
        previously occuring values
        :return: iterator of cells
        """
        assert self._parent_translation is not None, \
            "Parent translation must be set"
        values = set()
        for cell in self.source_column:
            value = cell.value_without_whitespace
            if value in values:
                yield cell
            values.add(value)


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

class TranslationDialog(QtW.QDialog):
    """
    Table widget containing columns and options to manipulate them
    """

    def __init__(self, settings):
        print('Translation Dlg began')
        super().__init__()
        source_sheet = settings[SOURCE_SHEET_KEY]
        target_sheet = settings[TARGET_SHEET_KEY]
        source_start = settings[SOURCE_START_KEY]
        target_start = settings[TARGET_START_KEY]
        assert isinstance(source_sheet, (Office.get_sheet_class(), str, int))
        assert isinstance(target_sheet, (Office.get_sheet_class(), str, int))
        assert isinstance(source_start, (int, str)), source_start
        assert isinstance(target_start, (int, str)), target_start
        # get Sheet obj from name or index if needed
        if not isinstance(source_sheet, Office.get_sheet_class()):
            source_sheet = model[source_sheet]
        if not isinstance(target_sheet, Office.get_sheet_class()):
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
        self._final_settings = None
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.show()

        def ok():
            """Function to confirm selections and create Translation"""
            self.accept()

        def back():
            """Function to resume prior dialog and close self"""
            self.reject()

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

    def _get_source_columns(self):
        """
        Returns list of source column names
        If source column header is empty, that column is not included.
        :return: list
        """
        assert isinstance(self.source_sheet, Sheet)
        return [cell.string for cell in self.source_sheet.get_row(0)
                if cell.string]  # include only if header is not empty

    def _get_target_columns(self):
        """
        Returns list of target column names
        :return: list
        """
        assert isinstance(self.target_sheet, Sheet)
        return [cell.value for cell in self.target_sheet.get_row(0)
                if cell.string]  # include only if header is not empty

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
            dict_name = SOURCE_COLUMN_NAME_KEY

            def __init__(self, table, start_value=NONE_STRING):
                super().__init__()
                self.table = table
                self.setToolTip('Select column to use as source')
                self.addItems(table.source_columns + [NONE_STRING])
                self.setCurrentText(start_value)
                # todo: add margins to text box?
                # It's rather close to the left side.

            @property
            def value(self):
                return self.currentText()

        class WhiteSpaceCheckbox(QtW.QCheckBox):
            name = 'Check for Whitespace'
            dict_name = WHITESPACE_CHK_KEY

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
            dict_name = DUPLICATE_CHK_KEY

            def __init__(self, table, start_value=False):
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

        @property
        def settings(self):
            """
            Returns list of column translation settings dicts.
            Returned dictionary is a list of dictionaries.
            Interior dictionaries have setting name as key.
            At time of this writing, interior dict looks like:
            {
                TARGET_COLUMN_KEY: < col name >
                SOURCE_COLUMN_KEY: < col name >
                WHITESPACE_CHECK_KEY: < bool >
                DUPLICATE_CHECK_KEY: < bool >
            }
            :return: list
            """

            def combine_dicts(*dicts):
                d = {}
                [d.update(dict__) for dict__ in dicts]
                return d

            translation_dicts = [
                # return a list of dictionaries with widget key and value
                combine_dicts(
                    {
                        self.cellWidget(y, x).dict_name:
                            self.cellWidget(y, x).value
                        for x in range(len(self.option_widget_classes))
                    },
                    {
                        # since the tgt col is not in option_widget_classes,
                        # it needs to be added here.
                        TARGET_COLUMN_NAME_KEY: tgt_col_name
                    }
                )
                for y, tgt_col_name in enumerate(self.target_columns)
            ]
            # remove dictionaries whose source is none
            for dict_ in translation_dicts:
                if dict_[SOURCE_COLUMN_NAME_KEY] == NONE_STRING:
                    translation_dicts.remove(dict_)
            return translation_dicts

    @property
    def settings(self):
        """
        Returns settings dictionary
        :return: dict
        """
        return {
            COLUMN_TRANSLATIONS_KEY: self.table.settings,
        }


class PreliminarySettings(QtW.QDialog):
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
                self.default_strings = default_values + tuple(self.defaults)
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

        @property
        def value(self):
            return self.text()

    class ImportSheetField(SheetField):
        """Gets name of sheet to import from"""
        dict_string = SOURCE_SHEET_KEY
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
        dict_string = TARGET_SHEET_KEY
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
        dict_string = SOURCE_START_KEY
        side_string = 'Import sheet start line'

        def gui_setup(self):
            self.setToolTip('Index of first row to be imported')
            self.setPlaceholderText('Import start row')

    class ExportSheetStartLine(StartLineField):
        """Gets index of line to start writing to"""
        dict_string = TARGET_START_KEY
        side_string = 'Export sheet start line'

        def gui_setup(self):
            self.setToolTip('Index of first row to be written to on target '
                            'sheet')
            self.setPlaceholderText('Export start row')

    class CancelButton(QtW.QPushButton):
        """Cancels out of macro"""

        def __init__(self, cancel_func):
            super().__init__()
            self.setText('Cancel')
            # noinspection PyUnresolvedReferences
            self.clicked.connect(cancel_func)  # not error
            self.show()

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
            # in the future
            additional_default_values = []

            # create and add the field
            field = field_class(start_str=start_str,
                                default_values=additional_default_values)
            assert isinstance(field, self.SettingField)
            self.fields.append(field)
            grid.add_row(field.side_string, field)
        # add ok and cancel buttons

        grid.add_row(self.CancelButton(lambda: self.reject()),
                     OkButton(self._ok))
        # todo: limit / freeze size of window
        self.setWindowTitle(APP_WINDOW_TITLE)

    def _ok(self):
        """
        Method called when user clicks 'ok' button on Preliminary
        Settings Widget.
        Creates AssociationTableWidget and passes it the created
        settings dictionary.
        """
        # check that entered sheets exist
        if any([not field.check_valid() for field in self.fields]):
            # field.check_valid displays info dialogs to user
            # if not valid.
            return  # does not move on if any fields are not valid
        self.setWindowTitle('')  # allow next widget to use the same title
        self.accept()

    @property
    def settings(self):
        """
        Gets dictionary of values stored in each field
        :return: dict
        """
        return {field.dict_string: field.value for field in self.fields}


class FinalSettings(QtW.QDialog):
    def __init__(self, settings):
        assert isinstance(settings, (dict, Settings)), \
            'expected dict or Settings, got instead: %s' % settings
        print('Final Settings dlg began')
        super().__init__()
        self._settings = settings

        field_classes = [
            self.DuplicateActionOption,
            self.WhitespaceOption,
        ]

        def back():
            self.setWindowTitle('')  # free up title
            self.prior_widget.resume()
            self.reject()

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
            self.host = host

            def apply():
                self.host.accept()

            # noinspection PyUnresolvedReferences
            self.clicked.connect(apply)  # not an error
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
        dict_str = DUPLICATE_ACTION_KEY
        side_string = 'Action for duplicates'

    class WhitespaceOption(MenuOption):
        options = 'Do nothing', 'Highlight', 'Remove whitespace'
        default_option = 'Highlight'
        tool_tip = 'Select action to be taken for cells containing whitespace'
        dict_str = WHITESPACE_ACTION_KEY
        side_string = 'Action for whitespace'

    @property
    def settings(self):
        """
        Returns grand collection of all settings inputted by user
        :return: dict
        """
        return {option.dict_str: option.value for option in self.fields}


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
        assert all([isinstance(item, str)for item in (title, main, secondary)])
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
        # noinspection PyUnresolvedReferences
        self.clicked.connect(ok_function)  # not error
        self.setToolTip('Move to next page')
        self.show()


class BackButton(QtW.QPushButton):
    def __init__(self, back_function):
        super().__init__('Back')
        self.setToolTip('Go to last page')
        # noinspection PyUnresolvedReferences
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


class OS:
    """
    Handles interaction with different operating systems.

    This may not need to be a class, but any independent functions appear
    as their own macro, so this is instead its own class
    """
    if platform.system() not in ('Linux', 'Windows', 'Mac'):
        raise OSError('Operating System \'%s\' not supported. Supported'
                      'operating systems are Linux, Windows, and Mac')

    @staticmethod
    def get_app_data_path():
        # get method name that should return path
        data_path_func_name = '_get_%s_data_path' % platform.system().lower()
        if hasattr(OS, data_path_func_name):
            data_path_func = getattr(OS, data_path_func_name)
        else:
            raise AttributeError('Could not find %s function in OS class'
                                 % data_path_func_name)
        return data_path_func()

    @staticmethod
    def _get_linux_data_path():
        """
        Gets data folder path for macro on Linux system.
        :return: str path
        """
        home_folder_path = os.getenv('HOME')
        return os.path.join(home_folder_path, '.' + APP_FOLDER_NAME)

    @staticmethod
    def _get_windows_data_path():
        """
        Gets data folder path for macro on Windows system.
        :return: str path
        """
        app_folder_path = os.getenv('APPDATA')
        return os.path.join(app_folder_path, APP_FOLDER_NAME)

    @staticmethod
    def _get_mac_data_path():
        """
        Gets data folder path for macro on Mac system.
        :return: str path
        """
        raise NotImplementedError('have not yet set up mac path')


class Files:
    """
    Handles retrieval and use of macro's files
    """
    file_creation_permission = False

    @staticmethod
    def get_file(relative_path, create_if_absent):
        """
        Returns file from relative path string.
        If not present, creates it if 'create_if_absent' is True,
        or returns None
        :param relative_path: path from macro root
            May either be string, tuple, or list.
        :param create_if_absent: whether file should be created if
        it is not present at specified path.
        """
        assert isinstance(relative_path, (str, list, tuple))
        if not isinstance(relative_path, str):
            # if not a string, turn it into one
            relative_path = os.path.join(*relative_path)


class Settings:
    settings_file_name = 'settings.ser'

    def __init__(self, macro_folder):
        print('created settings')
        self.file_path = os.path.join(macro_folder, self.settings_file_name)
        self._settings_dict = {}
        self.load()

    def __getitem__(self, item):
        return self._settings_dict[item]

    def __setitem__(self, key, value):
        self._settings_dict[key] = value

    def __delitem__(self, key):
        del self._settings_dict[key]

    def __contains__(self, item):
        return item in self._settings_dict

    def __repr__(self):
        return 'Settings(%s)' % self._settings_dict

    def save(self):
        """
        Saves settings in settings file.
        :return: bool of whether saving was successful
        """
        try:
            self.saved_settings = self._settings_dict
        except IOError:
            print('Saving Settings was unsuccessful.')
            print(IOError.strerror)
            return False
        else:
            print('Saved Settings Successfully.')
            return True

    def load(self):
        """
        Loads settings from settings file in file path
        :return bool of whether loading was successful
        """
        try:
            self._settings_dict = self.saved_settings
        except IOError:
            self._settings_dict = {}
            return False
        else:
            return True

    def update(self, dict_):
        assert isinstance(dict_, dict), 'expected dict, got: %s' % dict_
        self._settings_dict.update(dict_)

    @property
    def saved_settings(self):
        """
        Gets settings dictionary if one exists, otherwise returns
        an empty dictionary.
        Will raise IOError if this could not be accomplished.
        :return: dict
        """
        try:
            with open(self.file_path, 'r') as settings_file:
                settings = pickle.load(settings_file)
        except IOError and FileNotFoundError:
            print(IOError.strerror)
            raise IOError('Could not load settings from existing file')
            # todo: if cannot find file, ask to create it.
        else:
            return settings

    @saved_settings.setter
    def saved_settings(self, new_settings):
        """
        Stores settings dictionary.
        Will ask permission from user and try to create folder + file
        if needed.
        Will raise IOError if this could not be accomplished.
        :param new_settings: dict
        """
        try:
            with open(self.file_path, 'w') as settings_file:
                pickle.dump(new_settings, settings_file)
        except IOError:
            print('could not save settings to file')
            print(IOError.strerror)
            raise IOError('could not save settings to file')


def lead_app():
    """
    Main lead sheet management macro.
    Calls each dialog in turn and then creates and applies Translation.
    """
    # flow:
    # preliminary settings ->
    # association table ->
    # final settings / info
    # push data to target
    # close / display exit message
    print('started pyleadsmacro')
    print('Python version %s.%s.%s %s. serial: %s' % sys.version_info)
    app = QtW.QApplication([''])  # expects list of strings.
    print('started app')

    try:
        # get settings
        settings = Settings(OS.get_app_data_path())
        # get settings from prelim dialog
        run = True
        step = 0

        dialog_classes = [
            PreliminarySettings,
            TranslationDialog,
            FinalSettings
        ]
        while run:
            dlg = dialog_classes[step](settings)  # create dlg for current step
            result = dlg.exec_()  # run dlg and get result.
            settings.update(dlg.settings)
            if result:  # if user accepted, go to next step
                step += 1
            else:  # otherwise, go back.
                step -= 1
            if step < 0:  # if user has cancelled out of first dlg
                run = False
            elif step >= len(dialog_classes):  # if user has accepted last dlg
                break

        if run:  # if run is still ongoing
            translation = Translation(  # create translation
                source_sheet=model[settings[SOURCE_SHEET_KEY]],
                target_sheet=model[settings[TARGET_SHEET_KEY]],
                source_start_row=settings[SOURCE_START_KEY],
                target_start_row=settings[TARGET_START_KEY],
                column_translations=settings[COLUMN_TRANSLATIONS_KEY],
                dialog_parent=dlg,  # there's no way for this to be reached
                #  without dlg being assigned.
                duplicate_action=settings[DUPLICATE_ACTION_KEY],
                whitespace_action=settings[WHITESPACE_ACTION_KEY]
            )
            translation.commit()  # move cell values

            InfoMessage(  # tell user translation has been applied
                parent=dlg,
                title='Macro Finished',
                main='Finished moving cell values'
            )

        settings.save()  # save settings for next run
    except SystemExit:
        print('SystemExit raised')
        print('Exited macro')
        app.quit()
        # let macro exit without displaying an error


# create model handler object and in doing so,
# check PyUno model is a Workbook
model = Office.get_model()

if __name__ == '__main__':
    lead_app()
