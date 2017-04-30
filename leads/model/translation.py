"""
Module holding Translation class and associated methods and classes
"""

from .sheets import Sheet, Column, Cell, DEFAULT_COLOR
from .colors import DUPLICATE_CELL_COLOR, DUPLICATE_ROW_COLOR, \
        WHITESPACE_CELL_COLOR, WHITESPACE_ROW_COLOR

WHITESPACE_REMOVE_STR = 'Remove Whitespace'
WHITESPACE_HIGHLIGHT_STR = 'Highlight'
WHITESPACE_IGNORE_STR = 'Do nothing'

DUPLICATE_REMOVE_ROW_STR = 'Remove row'
DUPLICATE_HIGHLIGHT_STR = 'Highlight'
DUPLICATE_IGNORE_STR = 'Do nothing'


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
            source_start_row=1,
            target_start_row=1,
            whitespace_action=WHITESPACE_HIGHLIGHT_STR,
            duplicate_action=DUPLICATE_HIGHLIGHT_STR,
            read_log: bool=False,
            write_log: bool=False,
            log_group: str=None,
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
        self._row_deletions = set()
        self._src_cell_transforms = {}
        self._tgt_cell_transforms = {}
        self._source_start_row = source_start_row
        self._target_start_row = target_start_row
        self._whitespace_action = whitespace_action
        self._duplicate_action = duplicate_action
        self.read_log = read_log
        self.write_log = write_log
        self.log_group = log_group
        self.row_log = RowLog(OS.get_log_dir_path()) if \
            read_log or write_log else None
        self._source_sheet.take_snapshot()  # take snapshot of source sheet
        # create column translations from passed list of dicts
        # in settings
        self._column_translations = []
        self.add_column_translation(*column_translations)

        self.translation_rows = {}  # y_index: set(x_indices)
        self.cell_translation_generators = []  # x_index: generator
        self.cell_translations = {}  # src_pos: CellTranslation

        self._get_cell_generators()
        self._generate_cell_translations()
        self._source_sheet.discard_snapshot()  # we're done with source sheet

        if self.duplicate_action == DUPLICATE_HIGHLIGHT_STR:
            self._highlight_translation_rows_with_duplicates()
        elif self.duplicate_action == DUPLICATE_REMOVE_ROW_STR:
            self._remove_translation_rows_with_duplicates()

        if self.whitespace_action == WHITESPACE_HIGHLIGHT_STR:
            self._highlight_translation_rows_with_whitespace()
        elif self.whitespace_action == WHITESPACE_REMOVE_STR:
            self._remove_whitespace_in_translation_rows()

    def commit(self):
        print('committing translations')
        self.target_sheet.take_snapshot()
        self.clear_target()
        self._apply_translation_rows()
        if self.write_log:  # write log if that setting is set by user.
            self.row_log.make_log(self.log_group, self.target_sheet)
        self.target_sheet.write_snapshot()

    def _apply_translation_rows(self):
        for y in self.translation_rows:
            t_row = self.translation_rows[y]
            assert isinstance(t_row, TranslationRow)
            t_row.apply(self.target_sheet, y)

    def _get_cell_generators(self):
        for column_translation in self.column_translations:
            assert isinstance(column_translation, ColumnTranslation)
            self.cell_translation_generators.append(
                column_translation.get_generator())

    def _generate_cell_translations(self):
        print('mapping row translations')
        y = self._source_start_row
        while any([generator.has_next() for generator in
                   self.cell_translation_generators]):
            row = TranslationRow()
            for generator in self.cell_translation_generators:
                assert isinstance(generator, CellGenerator)
                if not generator.has_next():
                    continue
                cell_translation = generator.next()
                self.cell_translations[cell_translation.src_pos] = \
                    cell_translation
                row.add_cell_translation(cell_translation)
            self.translation_rows[y] = row
            y += 1
        print('done mapping row translations')

    def _highlight_translation_rows_with_whitespace(self):
        whitespace_positions = list(self.get_whitespace_positions())
        assert isinstance(whitespace_positions, list)
        for item in whitespace_positions:
            assert isinstance(item, tuple), 'got: %s' % item
            assert len(item) == 2, 'got: %s' % item
        for pos in whitespace_positions:
            try:
                cell_t = self.cell_translations[pos]
            except KeyError:
                continue
            assert isinstance(cell_t, CellTranslation)
            row = cell_t.row
            assert isinstance(row, TranslationRow)
            row.color_cell_and_row(
                pos[0],
                WHITESPACE_CELL_COLOR,
                WHITESPACE_ROW_COLOR,
            )
        self._whitespace_feedback(whitespace_positions)

    def _remove_whitespace_in_translation_rows(self):
        whitespace_positions = list(self.get_whitespace_positions())
        for pos in whitespace_positions:
            try:
                cell_t = self.cell_translations[pos]
                assert isinstance(cell_t, CellTranslation)
                cell_t.add_transform(lambda cell: cell.remove_whitespace())
            except KeyError:
                continue
        self._whitespace_feedback(whitespace_positions)

    def _highlight_translation_rows_with_duplicates(self):
        duplicate_positions = list(self.get_duplicate_positions())
        for pos in duplicate_positions:
            try:
                cell_t = self.cell_translations[pos]
            except KeyError:
                continue
            assert isinstance(cell_t, CellTranslation)
            row = cell_t.row
            assert isinstance(row, TranslationRow)
            row.color_cell_and_row(
                pos[0],
                DUPLICATE_CELL_COLOR,
                DUPLICATE_ROW_COLOR
            )
        self._duplicates_feedback(duplicate_positions)

    def _remove_translation_rows_with_duplicates(self):
        duplicate_positions = list(self.get_duplicate_positions())
        for pos in duplicate_positions:
            try:
                cell_t = self.cell_translations[pos]
            except KeyError:
                continue
            row = cell_t.row
            for y in self.translation_rows:
                if self.translation_rows[y] is row:
                    del self.translation_rows[y]
                    break
        self._duplicates_feedback(duplicate_positions)

    def get_duplicate_positions(self):
        """
        Returns lists of tuples of positions
        :return: iterator of tuples
        """
        print('looking for duplicate cells')
        for column_translation in self._column_translations:
            assert isinstance(column_translation, ColumnTranslation)
            if not column_translation.check_for_duplicates:
                continue
            for duplicate_cell in \
                    column_translation.get_duplicate_source_cells():
                assert isinstance(duplicate_cell, Cell)
                yield duplicate_cell.position
        print('done looking for duplicates')

    def get_whitespace_positions(self):
        """
        Returns lists of tuples of positions
        :return: iterator of tuples
        """
        print('looking for whitespace in cells')
        for column_translation in self._column_translations:
            assert isinstance(column_translation, ColumnTranslation)
            if not column_translation.check_for_whitespace:
                continue
            for cell in column_translation.get_whitespace_source_cells():
                yield cell.position
        print('done looking for whitespace')

    def _confirm_overwrite(self):
        reply = QMessageBox.question(
            self._dialog_parent,
            'Overwrite Cells?',
            'Cells on the target sheet will be overwritten.\n'
            'Proceed?',
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        return reply == QMessageBox.Yes

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
            # if source is null, continue
            if source_column_i == -1 or source_column_name == NONE_STRING:
                continue
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
                    if self._confirm_overwrite:
                        print('confirm dlg')
                        proceed = self._confirm_overwrite()
                        if not proceed:
                            return False
                    user_ok = True
                cell.value = ''
                cell.set_color(DEFAULT_COLOR)

    def _whitespace_feedback(self, whitespace_positions):
        """
        Reports to user on whitespace removals.
        Written to be called by _add_whitespace_cell_transforms method
        after whitespace transforms have been added.
        :param whitespace_positions:
        """
        if not whitespace_positions:
            return
        print('giving whitespace feedback')
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
            parent=self._dialog_parent,
            title='Whitespace Found',
            main='Whitespace found in %s cells' % len(
                whitespace_positions),
            secondary=secondary_string,
            detail=self._position_report(*whitespace_positions)
        )

    def _duplicates_feedback(
            self,
            duplicate_positions
    ) -> None:
        """
        Provides feedback to user about duplicates and actions taken
        regarding said duplicates.
        :param duplicate_positions: iterable of duplicate_positions
        """
        if not duplicate_positions or \
                self.duplicate_action == DUPLICATE_IGNORE_STR:
            return
        print('giving duplicates feedback')
        secondary_string = ''
        if self.duplicate_action == DUPLICATE_HIGHLIGHT_STR:
            secondary_string = '%s Cell values were highlighted in ' \
                               'checked columns' % len(duplicate_positions)
        elif self.duplicate_action == DUPLICATE_REMOVE_ROW_STR:
            n_rows_w_duplicates = len(set(
                [pos[1] for pos in duplicate_positions]))
            secondary_string = '%s Cell rows containing duplicate ' \
                               'values were removed' % n_rows_w_duplicates
        InfoMessage(
            parent=self._dialog_parent,
            title='Duplicate Values',
            main='%s Duplicate cell values found' % len(duplicate_positions),
            secondary=secondary_string,
            detail=self._position_report(*duplicate_positions)
        )

    def _position_report(self, *src_positions):
        """
        Converts iterable of positions into a more user-friendly
        report.
        output should consist of a list of row numbers, each with
        the names of the column containing passed position
        :param positions: tuples (int x, int y)
        :return: str
        """

        rows = []  # list of row indices in report.
        # This keeps the columns in order.
        row_columns = {}  # dictionary of string lists
        for x, y in src_positions:
            column_name = self._source_sheet.get_column(x).name
            y += 1  # convert to office 1-base index
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
            bool(source_column_name is None)
        ):
            raise ValueError(
                'Source column index or name must be passed, but not both. '
                'Got args source_column_i: %s (%s) and source_column_name: %s'
                ' (%s) respectively'
                % (source_column_i, source_column_i.__class__.__name__,
                   source_column_name, source_column_name.__class__.__name__))
        if (
            bool(target_column_i is None) ==
            bool(target_column_name is None)
        ):
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

    def get_generator(self):
        return CellGenerator(
            src_col=self.source_column,
            tgt_col=self.target_column,
            start_index=self._parent_translation.source_start_row
        )

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
        previously occurring values
        :return: iterator of cells
        """
        assert self._parent_translation is not None, \
            "Parent translation must be set"
        values = set()
        for cell in self.source_column:
            value = cell.value_without_whitespace
            # if cell's value is in set of existing values, return cell.
            if value in values:
                yield cell
            else:  # otherwise, check if cell is in log
                parent = self._parent_translation
                if parent.read_log:  # if option is set
                    parent.row_log.find_duplicates(
                        value, parent.log_group, self.target_column_name
                    )
                values.add(value)  # add value to set of existing values


class CellGenerator:
    def __init__(self, src_col, tgt_col, start_index):
        if not isinstance(src_col, Column):
            raise TypeError('expected Column. got: %s' % src_col)
        if not isinstance(tgt_col, Column):
            raise TypeError
        if not isinstance(start_index, int):
            raise TypeError
        self.tgt_col = tgt_col
        self.src_col = src_col
        self.i = start_index
        self.end_index_exclusive = len(src_col)

    def has_next(self):
        if self.i < self.end_index_exclusive:
            return True

    def next(self):
        cell_translation = CellTranslation(
            cell=self.src_col.get_cell_by_index(self.i),
            src_x=self.src_col.index,
            tgt_x=self.tgt_col.index
        )
        self.i += 1
        return cell_translation


class TranslationRow:
    def __init__(self):
        self.cell_translations = []

    def add_cell_translation(self, *translations):
        for cell_translation in translations:
            cell_translation.row = self
            self.cell_translations.append(cell_translation)

    def color_cell_and_row(self, cell_x, cell_color, row_color):
        for cell_t in self.cell_translations:
            assert isinstance(cell_t, CellTranslation)
            if cell_t.src_x != cell_x:
                cell_t.add_transform(
                    lambda cell:
                    cell.set_color(row_color) if
                    cell.get_color() == -1  # if cell is default color
                    else None
                )
            else:
                cell_t.add_transform(lambda cell: cell.set_color(cell_color))

    def apply(self, tgt_sheet, y):
        for cell_t in self.cell_translations:
            assert isinstance(cell_t, CellTranslation)
            cell_t.apply(tgt_sheet, y)


class CellTranslation:
    row = None

    def __init__(self, cell, src_x, tgt_x):
        self.cell, self.src_x, self.tgt_x = cell, src_x, tgt_x
        self.transforms = []

    def apply(self, tgt_sheet, y_pos):
        if not isinstance(tgt_sheet, Sheet):
            raise TypeError
        if not isinstance(y_pos, int):
            raise TypeError
        tgt_cell = tgt_sheet.get_cell((self.tgt_x, y_pos))
        tgt_cell.value = self.cell.value
        [transform(tgt_cell) for transform in self.transforms]

    def add_transform(self, transform):
        assert hasattr(transform, '__call__')
        self.transforms.append(transform)

    @property
    def src_pos(self):
        return self.cell.position


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