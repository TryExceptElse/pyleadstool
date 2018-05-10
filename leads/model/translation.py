"""
Module holding Translation class and associated methods and classes
"""

import logging
import typing as ty

from collections import namedtuple
from datetime import datetime, timedelta

try:
    from .records import RecordCollection
except ImportError:
    RecordCollection = None
from .sheets import Sheet, Column, Cell, Row, DEFAULT_COLOR, NONE_STRING
from .colors import DUPLICATE_CELL_COLOR, DUPLICATE_ROW_COLOR, \
        WHITESPACE_CELL_COLOR, WHITESPACE_ROW_COLOR

WHITESPACE_REMOVE_STR = 'Remove Whitespace'
WHITESPACE_HIGHLIGHT_STR = 'Highlight'
WHITESPACE_IGNORE_STR = 'Do nothing'

DUPLICATE_REMOVE_ROW_STR = 'Remove row'
DUPLICATE_HIGHLIGHT_STR = 'Highlight'
DUPLICATE_IGNORE_STR = 'Do nothing'

SOURCE_COLUMN_NAME_KEY = 'source_column_name'
TARGET_COLUMN_NAME_KEY = 'target_column_name'
SOURCE_COLUMN_INDEX_KEY = 'source_column_i'
TARGET_COLUMN_INDEX_KEY = 'target_column_i'

# json log keys
LOG_DATE_TIME_KEY = 'datetime'
LOG_TGT_COLUMNS_KEY = 'tgt_col'
LOG_TGT_SHEET_NAME = 'tgt_sheet_name'
LOG_SRC_SHEET_NAME = 'src_sheet_name'


class Translation:
    """
    Handles movement of data from source to target sheets and applies
    modifications
    """

    def __init__(
            self,
            source_sheet: Sheet,
            target_sheet: Sheet,
            column_translations=None,
            source_start_row=1,
            target_start_row=1,
            overwrite_confirm_func=None,
            record_to_read=None,
    ) -> None:
        logger = logging.getLogger(__name__)
        logger.info('Created Translation. src={}, tgt={}'
                    .format(source_sheet, target_sheet))
        if not isinstance(source_sheet, Sheet):
            raise TypeError('Source sheet should be a Sheet, got: %s'
                            % repr(source_sheet))
        if not isinstance(target_sheet, Sheet):
            raise TypeError('Target sheet should be a Sheet, got: %s'
                            % repr(source_sheet))
        self._source_sheet: Sheet = source_sheet
        self._target_sheet: Sheet = target_sheet
        self._source_start_row = source_start_row
        self._target_start_row = target_start_row
        self.overwrite_confirm_func = overwrite_confirm_func
        self.reading_log: 'RecordCollection' = record_to_read
        # create column translations from passed list of dicts
        # in settings
        self._column_translations: ty.List['ColumnTranslation'] = []
        self.add_column_translation(*column_translations)

        logging.debug('finished creating translation')

    def commit(self) -> 'CommitReport':
        logger = logging.getLogger(__name__)
        logger.info('Committing translation. src={}, tgt={}'
                    .format(self.source_sheet, self.target_sheet))
        print('committing translations')
        self._target_sheet.take_snapshot()
        self.clear_target()
        report = CommitReport()  # make report to store results in
        report.validation_report = self.check()
        report.commit_datetime = datetime.utcnow()
        for entry in self.source_sheet_entries:
            assert isinstance(entry, Entry), entry

        self._target_sheet.write_snapshot()
        return report

    def check(self) -> 'ValidationReport':
        """
        Checks that data in cells to be translated is valid.
        :return: ValidationReport
        """
        logger = logging.getLogger(__name__)
        logger.info('Checking translation. '
                    f'src={self.source_sheet}, tgt={self.target_sheet}')
        data = _TranslationData()
        report = ValidationReport()
        for entry in self.source_sheet_entries:
            assert isinstance(entry, Entry)
            for col_translation, cell_data in entry.items():
                assert isinstance(col_translation, ColumnTranslation), \
                    col_translation
                assert isinstance(cell_data, CellData), cell_data
                # get validator and validate cell data
                validator: 'Validator' = col_translation.validator
                issues = validator.validate(cell_data, data, self.reading_log)
                # add issues returned by validator to ValidationReport
                assert isinstance(issues, ty.Container['Issue']), issues
                report.add_line(*issues)
        return report

    @property
    def source_sheet_entries(self) -> ty.Iterable['Entry']:
        """
        Generates entries from source sheet.
        :return: Entry generator
        """
        for row in self.source_sheet.rows:
            entry = self._make_entry(row)
            yield entry

    def _make_entry(self, row: 'Row') -> 'Entry':
        """
        Creates entry from source sheet row.
        :param row: Row
        :return: Entry
        """
        entry = Entry()
        for column_translation in self.column_translations:
            cell: 'Cell' = row[column_translation.source_column_i]
            cell_data: CellData = column_translation.cell_data_type(cell)
            entry[column_translation] = cell_data
        return entry

    def _confirm_overwrite(self):
        """
        If an overwrite confirmation function has been passed, calls it
        to get permission to overwrite cell values in target sheet.

        If one has not been passed, just overwrites the target.

        This method should be called at most once per translation,
        as the result should be stored.
        :return: None
        """
        logger = logging.getLogger(__name__)
        logger.debug('confirming overwrite of cells in tgt sheet')
        if self.overwrite_confirm_func:
            return self.overwrite_confirm_func()
        else:
            return True

    def add_column_translation(
            self, *translations: 'ColumnTranslation') -> None:
        """
        Adds translation to queue which when applied, copies cell data
        from source column to target column.
        :param translations: ColumnTranslation any number of translations.
        """

        logger = logging.getLogger(__name__)
        logger.debug('adding column translation(s)')

        for translation in translations:
            logger.debug(f'adding {translation}')
            self._column_translations.append(
                translation
            )

    def clear_target(self):
        """
        Clears target sheet of conflicting cell data.
        Raises dialog for user to ok if anything is to be deleted.
        """

        logger = logging.getLogger(__name__)
        logger.debug('Clearing target sheet of any conflicting cell data')

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

    @property
    def source_sheet(self):
        """
        Gets source sheet.
        :return: Sheet
        """
        return self._source_sheet

    @property
    def target_sheet(self):
        """
        Gets target sheet.
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
        Sets the row index at which cells begin to be copied.
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._source_start_row = new_index

    @property
    def target_start_row(self):
        """
        Gets the row index at which cells begin to be written to.
        :return: int
        """
        return self._target_start_row

    @target_start_row.setter
    def target_start_row(self, new_index):
        """
        Sets the row index at which cells begin to be written to.
        :param new_index: int
        """
        assert isinstance(new_index, int)
        self._target_start_row = new_index

    @property
    def column_translations(self):
        """
        Returns list of column translations.
        :return: list of ColumnTranslations
        """
        return self._column_translations.copy()


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
            validator: 'Validator'=None,
    ) -> None:
        # Check that source column name xor index has been passed.
        if bool(source_column_i is None) == bool(source_column_name is None):
            raise ValueError(
                'Source column index or name must be passed, but not both. '
                'Got args source_column_i: %s (%s) and source_column_name: %s'
                ' (%s) respectively'
                % (source_column_i, source_column_i.__class__.__name__,
                   source_column_name, source_column_name.__class__.__name__))
        # Check that target column name xor index has been passed.
        if bool(target_column_i is None) == bool(target_column_name is None):
            raise ValueError(
                'Target column index or name must be passed, but not both. '
                'Got args target_column_i: %s (%s) and target_column_name: %s'
                '(%s)'
                % (target_column_i, target_column_i.__class__.__name__,
                   target_column_name, target_column_name.__class__.__name__)
            )
        self._validator = validator or BasicValidator()
        self._parent_translation = parent_translation
        self._target_column_i = target_column_i
        self._source_column_i = source_column_i
        self._target_column_name = target_column_name
        self._source_column_name = source_column_name

    # source sheet getters / setters

    @property
    def source_sheet(self) -> Sheet:
        """
        Gets source sheet, from which cells are retrieved.
        :return: Sheet
        """
        return self._parent_translation.source_sheet

    @property
    def source_column_i(self) -> int:
        """
        Gets source column identifier.
        :return: int
        """
        if self._source_column_i is not None:
            return self._source_column_i
        else:
            return self.source_column.index

    @source_column_i.setter
    def source_column_i(self, new_column: int):
        """
        Sets source column.
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
        Gets source column.
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
        Gets target sheet, to which cells are moved.
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

    @property
    def cell_data_type(self):
        return self._validator.cell_data_type

    @property
    def validator(self) -> 'Validator':
        return self._validator


class Entry(dict):
    """
    Stores data of a single row.

    Stored keys should be target column identifiers, values should
    be stored cell values.
    """

    def __setitem__(self, key: 'ColumnTranslation', value: 'CellData') -> None:
        if not isinstance(key, ColumnTranslation):
            raise TypeError(f'Expected ColumnTranslation as key, got: {key}')
        if not isinstance(value, CellData):
            raise TypeError(f'Expected CellData as value, got {value}')
        super().__setitem__(key, value)


class CellData:
    """
    Stores data from a single column in Entry.
    This class does nothing special, but subclasses may impose
    validation in the initialization method, and override
    comparison methods or similar.
    """

    def __init__(self, cell: 'Cell'):
        self.cell = cell

    @property
    def value(self):
        return self.cell.value


class _TranslationData:
    """
    Stores data related to a single check or commit.
    TranslationData is given to Validators when they are validating
    a cell so that they may optionally store data specific to a single
    check or commit
    """

    def __init__(self):
        self._d = {}

    def add_collection(self, validator: 'Validator', collection: ty.Container):
        if validator in self._d:
            raise ValueError(f"{validator} already present in {self}")
        self._d[validator] = collection

    def __getitem__(self, validator: 'Validator') -> ty.Container:
        if validator not in self._d:
            raise ValueError(
                f'{validator} not in {self}. Call add_collection first?')
        return self._d[validator]

    def __repr__(self) -> str:
        return f'_TranslationData[{self.__hash__()}]'


#######################################################################
# Reports:
#######################################################################


class CommitReport:
    def __init__(self):
        self._commit_datetime: datetime or None = None
        self._validation_report: ValidationReport or None = None

    @property
    def commit_datetime(self) -> datetime or None:
        return self._commit_datetime

    @commit_datetime.setter
    def commit_datetime(self, commit_datetime: datetime):
        if self.commit_datetime:
            raise ValueError('Commit Date-Time already set')
        self._commit_datetime = commit_datetime

    @property
    def validation_report(self) -> datetime or None:
        return self._validation_report

    @validation_report.setter
    def validation_report(self, report: 'ValidationReport'):
        if self._validation_report:
            raise ValueError('validation_report already set')
        self._validation_report = report


class ValidationReport:
    """
    Stores information produced by Validator.
    """
    def __init__(self):
        self.column_issues = {}  # issues, stored by entry column.
        self.row_issues = {}  # issues, stored by entry row.

    def add_line(self, *issue: 'Issue'):
        for issue_ in issue:
            row, col = issue_.cell.row, issue_.cell.column

            try:  # add to list of issues related to row
                self.row_issues[row].append(issue_)
            except KeyError:  # create new list for row
                self.row_issues[row] = [issue_]

            try:  # add to list of issues related to col
                self.column_issues[col].append(issue_)
            except KeyError:  # create new list for column
                self.column_issues[col] = [issue_]


# stores an issue with a single cell
Issue = namedtuple('Issue', ['cell', 'feedback'])


#######################################################################
# Validators:
#######################################################################


class Validator:
    """
    Handles a specific type of input, checking for unexpected data,
    and handles response to such data.
    """
    cell_data_type = CellData

    def __call__(self, *args, **kwargs) -> ty.Set['Issue']:
        return self.validate(*args, **kwargs)

    def validate(
            self,
            cell_data: CellData,
            translation_data: '_TranslationData',
            records: 'RecordCollection'=None
    ) -> ty.Set['Issue']:
        pass  # extended by subclasses


class BasicValidator(Validator):
    """
    Generic Validator, validating values stored in a column without
    special attributes.
    """
    def __init__(
            self,
            dup_chk: bool=True,
            white_chk: bool=True,
            min_dup_age: float=0
    ) -> None:
        self.check_for_duplicates: bool = dup_chk
        self.check_for_whitespace: bool = white_chk
        # duration after which a duplicate value is acceptable
        self._min_duplicate_age: float = min_dup_age

    def validate(
            self,
            cell_data: CellData,
            translation_data: '_TranslationData',
            records: 'RecordCollection'=None
    ) -> ty.Set['Issue']:
        issues: ty.Set['Issue'] = set()
        if self.check_for_whitespace and cell_data.cell.has_whitespace:
            cell = cell_data.cell
            issues.add(Issue(cell, f"{cell} has whitespace"))

        def find_duplicate() -> str:
            """
            Returns string describing position where
            cell_data is duplicated.
            Returns only the first duplicate found.
            :return: str
            """
            value = cell_data.cell.value_without_whitespace
            s = ''

            # check in previous cells in translation for duplicate
            try:
                checked_values = translation_data[self]
            except KeyError:
                checked_values = {}
                translation_data.add_collection(self, checked_values)

            assert isinstance(checked_values, dict), checked_values
            if value in checked_values:
                s = f'duplicate in earlier cell: {checked_values[value]}'

            # check in previous records of translations
            if records:
                pass  # TODO

            # add value + cell to checked values
            checked_values[value] = cell_data.cell

            return s

        duplicate = find_duplicate()  # get string indicating duplicate pos
        if self.check_for_duplicates and duplicate:
            cell = cell_data.cell
            issues.add(Issue(
                cell, f'{cell} contains a duplicate. ' + duplicate))

        return issues
