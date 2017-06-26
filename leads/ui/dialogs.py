"""
Module containing dialogs
"""
import datetime

from PyQt5.Qt import *

from .layout.record_entry_view import Ui_Dialog as RecordEntryViewLayout
from .layout.record_val_search import Ui_Dialog as RecordValSearchLayout
from .layout.record_view import Ui_Dialog as RecordViewLayout
from .layout.records import Ui_Dialog as RecordsViewLayout


class LeadsDialog(QDialog):
    def __init__(self, controller: 'Controller', model: 'Model'):
        super().__init__()
        self.controller = controller
        self.model = model


class RecordEntryViewDlg(LeadsDialog, RecordEntryViewLayout):
    """
    Class handling gui dialog allowing viewing of an entry in
    translation records.
    """

    def __init__(self, controller: 'Controller', model: 'Model'):
        super().__init__(controller, model)
        self.setupUi(self)

    # setup gui and connect actions to methods


class RecordValSearchDlg(LeadsDialog, RecordValSearchLayout):
    """
    Class handling searching of records for translation record
    entries containing specified value(s) in specified field(s)
    """
    window_title = 'Search Records'
    search_all_records_header = 'Searching All Records'
    search_specific_record_header_prefix = 'Searching Record of '
    search_n_records_header = 'Searching {} Records'

    def __init__(self, controller, model, *records):
        super().__init__(controller, model)
        self.setupUi(self)
        self.setWindowTitle(self.window_title)
        self.endDateTimeEdit.setDateTime(datetime.datetime.now())
        self.records = records if records else None
        self.headerLabel.setText(self.find_header_text())

    def find_header_text(self) -> str:
        if not self.records:
            return self.search_all_records_header
        if len(self.records) == 1:
            return self.search_specific_record_header_prefix + \
                   str(self.records[0].t)
        else:
            return self.search_n_records_header.format(len(self.records))


class RecordViewDlg(LeadsDialog, RecordViewLayout):
    """
    Class allowing viewing of a specific record and its contained entries
    """
    title_prefix = 'Translation Record of '

    def __init__(self, translation, controller, model):
        super().__init__(controller, model)
        self.setupUi(self)
        self.translation = translation
        self.translationRecordLabel.setText(self.find_title())

    def find_title(self):
        return self.title_prefix + str(self.translation.t)


class RecordsViewDlg(LeadsDialog, RecordsViewLayout):
    """
    Class allowing viewing of all translations in records,
    by campaign, date, and time.
    """
    window_title = 'All Records'

    def __init__(self, controller, model):
        super().__init__(controller, model)
        self.setupUi(self)
        self.setWindowTitle(self.window_title)
        self.endDate.setDateTime(datetime.datetime.now())
