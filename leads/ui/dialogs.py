"""
Module containing dialogs
"""
import datetime

from PyQt5.Qt import *

from .layout.record_entry_view import Ui_Dialog as RecordEntryViewLayout
from .layout.record_val_search import Ui_Dialog as RecordValSearchLayout
from .layout.record_view import Ui_Dialog as RecordViewLayout
from .layout.records import Ui_Dialog as RecordsViewLayout
from .layout.campaign_new import Ui_Dialog as NewCampaignLayout
from .layout.campaign_del import Ui_Dialog as DelCampaignLayout


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


# CAMPAIGN DIALOGS


class NewCampaignDlg(LeadsDialog, NewCampaignLayout):
    """
    Dialog prompting user to input name of new campaign to be created
    """
    window_title = 'New Campaign'

    def __init__(self, controller, model):
        super().__init__(controller, model)
        self.setupUi(self)
        self.setWindowTitle(self.window_title)

    def exec(self):
        super().exec()
        name = self.nameField.text()
        return name if name else False


class DelCampaignDlg(LeadsDialog, DelCampaignLayout):
    """
    Dialog prompting user to confirm that they wish to delete a
    campaign by entering the campaign's name and then pressing
    """
    window_title = 'Delete Campaign?'

    def __init__(self, controller, model, campaign):
        super().__init__(controller, model)
        self.campaign = campaign
        self._accepted = False
        self.setupUi(self)
        self.setWindowTitle(self.window_title)

        # format text for widgets that need the campaign name to be inserted.
        [widget.setText(widget.text().format(campaign.name)) for
         widget in (self.mainLabel, self.delButton)]
        self.nameField.setPlaceholderText(campaign.name)

        # connect buttons
        self.delButton.clicked.connect(self._delete_btn_pressed)
        self.cancelButton.clicked.connect(self.close)

    def _delete_btn_pressed(self):
        if self.nameField.text() == '':
            # create dialog informing user that no text was entered.
            title = 'No name entered.'
            main = 'The name field was left blank.\nTo ensure that the' \
                   'correct campaign is being deleted, type the name of' \
                   'the campaign to be deleted into the name field.'
            dlg = QMessageBox(QMessageBox.Information, title, main)
            dlg.setStyleSheet(self.styleSheet())
            dlg.exec()
            return
        elif self.nameField.text() != self.campaign.name:
            # create dialog informing user that the two did not match
            title = 'Names did not Match'
            main = 'The campaign name entered did not match the name ' \
                'of the campaign to be deleted'
            dlg = QMessageBox(QMessageBox.Information, title, main)
            dlg.setStyleSheet(self.styleSheet())
            dlg.exec()
            return
        else:
            self.accept()

    def accept(self):
        """
        Called when user hits enter while in dialog, or when 'Delete'
        is pressed.
        :return: None
        """
        self._accepted = True  # leave marker for use by confirmed property
        super().accept()

    @property
    def confirmed(self):
        """
        Returns true if user has confirmed deletion.
        :return: bool
        """
        return self.nameField.text() == self.campaign.name and self._accepted
