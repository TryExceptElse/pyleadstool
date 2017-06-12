"""

"""
from threading import Thread
from time import sleep
from PyQt5.Qt import *  # all classes from this module are named as QSomething

from leadmacro import Model as OfficeModel, Sheet, Column


UPDATE_CHECK_RATE = 1  # Hz

WHITESPACE_CHK_DEFAULT = True
DUPLICATE_CHK_DEFAULT = False


class UpdatingListModel(QStandardItemModel):
    """
    List model which can be extended to create a regularly updating
    """
    update_frq = 1  # Hz

    def __init__(self, parent):
        super().__init__(parent)
        self.current_items = set()
        self.update()
        # start watcher thread
        self.update_thread = Thread(
            target=self.watch_for_updates, daemon=True
        )
        self.update_thread.start()

    def watch_for_updates(self):
        """
        Method that regularly updates the model
        :return: None
        """
        while True:
            sleep(60 / UPDATE_CHECK_RATE)
            self.update()

    def item_getter(self):
        """
        Method that finds and returns a collection of items
        to be used in model.
        Must be overridden in subclasses.
        For best performance, should return a set.
        :return:
        """
        raise NotImplementedError

    def factory(self, item):
        """
        Method that takes a item returned by getter and produces an
        instance of a class extending QStandardItem.
        Must be overridden by subclasses.
        :return: ? extending QStandardItem
        """
        raise NotImplementedError

    def update(self) -> None:
        """
        Updates model with new items and removes old ones.
        :return: None
        """
        new_item_set = set(self.item_getter())
        if len(new_item_set) == 0:
            # if set is empty, place marker for user
            self.clear()
            self.appendRow(self.EmptyListMarkerItem())
        # add each item in new items that is not in current_items
        for model_item in self.children():
            assert isinstance(model_item, self.UpdatingModelItem)
            if model_item.item not in new_item_set:
                self.removeRow(model_item)
        # remove each item in current items that is not in new items
        for item in self.current_items:
            if item not in new_item_set:
                self.appendRow(self.factory(item))

    class UpdatingModelItem(QStandardItem):
        def __init__(self, item):
            super().__init__()
            self.item = item

    class EmptyListMarkerItem(QStandardItem):
        """
        This item displays a message to the user that no items could
        be found.
        """
        def __init__(self):
            super().__init__()
            self.setText('No Items')


class SheetListModel(QStandardItemModel):
    """
    Model to be used by the SheetList on the main window,
    displaying alphabetical list of currently open sheets in Office.
    """
    def __init__(self, office_model):
        super().__init__()
        self.office_model = office_model
        self.sheet_names = set()
        self._connected = None

        self.update()
        # start watcher thread
        self.update_thread = Thread(
            target=self.watch_for_updates, daemon=True
        )
        self.update_thread.start()

    def clear(self):
        super().clear()
        self.sheet_names.clear()

    def watch_for_updates(self):
        while True:
            sleep(60 / UPDATE_CHECK_RATE)
            self.update()

    def update(self):
        if self.office_model is not None:
            # this will clear items, so it must be set first.
            self._has_connection = True
            assert isinstance(self.office_model, OfficeModel), \
                self.office_model
            sheets_in_model = set(self.office_model.sheet_names)
            # remove old sheet items
            for row in self.children():
                assert isinstance(row, self.SheetItem)
                if row.sheet_name not in sheets_in_model:
                    self.removeRow(row.index())
            # add new sheet items
            for sheet_name in sheets_in_model:
                if sheet_name not in self.sheet_names:
                    self.sheet_names.add(sheet_name)
                    self.appendRow(self.SheetItem(sheet_name))
            self.sort(1)
        else:
            # if no way to connect to an office instance can be found,
            # office_model will be None
            self._has_connection = False

    @property
    def _has_connection(self):
        return self._connected

    @_has_connection.setter
    def _has_connection(self, connected: bool):
        if connected and not self._connected:
            self.clear()
        elif not connected and self._connected is not False:
            self.clear()
            self.appendRow(self.NoConnectionItem())

    class SheetItem(QStandardItem):
        """
        Individual item in sheet list model.
        """
        def __init__(self, sheet_name: str):
            super().__init__(sheet_name)
            self.sheet_name = sheet_name
            self.setText(sheet_name)

    class NoConnectionItem(QStandardItem):
        """
        This item displays a message to the user that no office
        connection could be found
        """
        def __init__(self):
            super().__init__()
            self.setText('No connection')


class CampaignListModel(UpdatingListModel):
    def __init__(self, collection):
        self.collection = collection
        super().__init__(None)

    def item_getter(self):
        return self.collection.campaigns

    def factory(self, item):
        return self.CampaignItem(item)

    class CampaignItem(UpdatingListModel.UpdatingModelItem):
        def __init__(self, campaign):
            super().__init__(campaign)
            self.setText(campaign.name)


class TranslationTableModel(QAbstractTableModel):
    """
    Data model to be used for displaying and manipulating translation
    settings
    """

    horizontal_headers = (
        'Source Column',
        'Duplicate Check',
        'Whitespace Check'
    )

    def __init__(self, data_model):
        super().__init__()
        self.model = data_model
        self._translation_entries = []  # stored in order
        self.update()

    def rowCount(self, parent):
        if self.model.source_sheet:
            return len(self.model.source_sheet.columns.names)
        else:
            return 0

    def columnCount(self, parent):
        """
        :type parent: QWidget
        """
        return 3

    def headerData(self, p_int, orientation, int_role=None):
        if int_role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.horizontal_headers[p_int]
        else:
            return QVariant()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        row_i, col_i = index.row(), index.column()
        entry = self._translation_entries[row_i]
        if col_i == 0:
            return entry.tgt_name
        elif col_i == 1:
            return entry.src_selector
        elif col_i == 2:
            return entry.dup_chk_selector
        elif col_i == 3:
            return entry.whitespace_chk_selector

    def update(self):
        if self.model.source_sheet is None:
            self._translation_entries = []
            return
        src_sheet = self.model.source_sheet
        tgt_sheet = self.model.target_sheet
        if not isinstance(src_sheet, Sheet):
            raise TypeError(
                'update(): model.source_sheet should have been a Sheet.'
                'Got instead: {}'.format(repr(src_sheet)))
        if not isinstance(tgt_sheet, Sheet):
            raise TypeError(
                'update(): model.target_sheet should have been a Sheet.'
                'Got instead: {}'.format(repr(src_sheet)))
        represented_tgt_rows = \
            {entry.tgt_name: entry for entry in self._translation_entries}
        # make updated list of entries, re-using existing entries if
        # possible, which will replace existing entry list.
        new_entry_list = []
        for tgt_col in tgt_sheet.columns:
            assert isinstance(tgt_col, Column)
            try:
                new_entry_list.append(represented_tgt_rows[tgt_col.name])
            except KeyError:
                new_entry = self.ColEntry(tgt_col, self.model)
                new_entry_list.append(new_entry)

        [entry.update for entry in new_entry_list]
        self._translation_entries = new_entry_list

    @property
    def translation_entries(self):
        return self._translation_entries

    class ColEntry:
        NONE_OPTION_TEXT = '--None--'

        def __init__(self, tgt_col: Column, data_model):
            super().__init__()
            self.tgt_col = tgt_col
            self.model = data_model
            self.src_selector = self.make_src_col_selector()
            self.dup_chk_selector = self.make_dup_chk_selector()
            self.whitespace_chk_selector = self.make_whitespace_chk_selector()

        def make_src_col_selector(self):
            src_sheet = self.model.source_sheet
            assert isinstance(src_sheet, Sheet)
            selector = QComboBox(self)
            selector.setToolTip(
                'Select the column of the source sheet to copy data from')
            selector.addItems(src_sheet.columns.names)  # add src options
            return selector

        def make_dup_chk_selector(self):
            selector = QCheckBox()
            selector.setChecked(DUPLICATE_CHK_DEFAULT)
            return selector

        def make_whitespace_chk_selector(self):
            selector = QCheckBox()
            selector.setChecked(WHITESPACE_CHK_DEFAULT)
            return selector

        def update(self):
            """
            Updates entry row items. Called on update of table model.
            :return:  None
            """
            src_sheet = self.model.source_sheet
            src_names = [name for name in src_sheet.columns.names]
            selector_model = self.src_selector.model()
            assert isinstance(selector_model, QStandardItemModel)
            for i, name in enumerate(src_names):
                if selector_model.item(i).text() != name:
                    break
            else:
                return  # if all options match column names, exit
            self.src_selector.clear()
            self.src_selector.addItems(src_names)
            self.src_selector.addItem(self.NONE_OPTION_TEXT)
            self.src_selector.setCurrentText(self.NONE_OPTION_TEXT)
            self.dup_chk_selector.setChecked(DUPLICATE_CHK_DEFAULT)
            self.whitespace_chk_selector.setChecked(WHITESPACE_CHK_DEFAULT)

        @property
        def tgt_name(self) -> str:
            """
            Returns name of target column.
            :return: str
            """
            return self.tgt_col.name

        @property
        def src_col(self):
            """
            Returns currently selected source column.
            :return: Column
            """
            col_name = self.src_selector.currentText()
            return self.model.source_sheet.get_column_by_name(col_name)

        @property
        def src_name(self) -> str:
            """
            Returns name of source column
            :return: str
            """
            return self.src_col.name

    class HeaderItem(QStandardItem):

        SRC_COL_HEADER = 'Source Column'
        WHITESPACE_CHK_HDR = 'Whitespace Check'
        DUPLICATE_CHK_HDR = 'Duplicate Check'

        def __init__(self):
            self.setData(0, self.SRC_COL_HEADER)
            self.setData(1, self.DUPLICATE_CHK_HDR)
            self.setData(2, self.WHITESPACE_CHK_HDR)