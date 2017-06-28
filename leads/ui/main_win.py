"""
Module containing the main window.
This class also serves as the view of the program.
"""
from PyQt5.Qt import *  # all objects in package are named as QWidget, etc

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from .dialogs import RecordValSearchDlg, RecordsViewDlg, \
    NewCampaignDlg, DelCampaignDlg
from .layout.mainwindow import Ui_MainWindow
from ..model.lead_model import Model

# Constants used in GUI

WHITESPACE_REMOVE_STR = 'Remove Whitespace'
WHITESPACE_HIGHLIGHT_STR = 'Highlight'
WHITESPACE_IGNORE_STR = 'Do nothing'

DUPLICATE_REMOVE_ROW_STR = 'Remove row'
DUPLICATE_HIGHLIGHT_STR = 'Highlight'
DUPLICATE_IGNORE_STR = 'Do nothing'


class MainWin(QMainWindow, Ui_MainWindow):
    """
    Main window class
    """

    def __init__(self, model: Model):
        super().__init__()
        self.setupUi(self)  # apply layout to this main window
        self._controller = None
        self.model = model
        # call to .show() occurs in _complete_gui() method,
        # after controller is set.

    def startup(self):
        """
        Performs actions that need to be carried out at beginning of run
        :return: None
        """
        if self.model.campaigns.is_empty:
            self.show_make_campaign_query_dlg()

    @property
    def controller(self):
        """
        Gets controller obj.
        :return: Controller
        """
        return self._controller

    @controller.setter
    def controller(self, controller):
        """
        Sets controller for view. Should only be called once.
        Setting the controller triggers completion of the gui,
        and connects actions to their respective methods.
        :param controller: Controller
        :return: None
        """
        if self.controller:
            print('Controller for main window has been set twice. This is odd')
        self._controller = controller
        self._complete_gui()

    def _complete_gui(self):
        self._setup_tool_bar()
        self._setup_sheet_list()
        self._setup_campaign_list()
        self._setup_translation_table()
        self.show()  # display main window to user

        self.startup()  # perform actions that need to be done at startup

    def _setup_tool_bar(self):
        self.actionApplyTranslations.triggered.connect(self.controller.apply)
        self.actionCheck.triggered.connect(self.controller.check)
        self.searchAction.triggered.connect(self.controller.search_records)
        self.viewRecordsAction.triggered.connect(self.controller.view_records)

    def _setup_sheet_list(self):
        self.sheetsList.setModel(self.model.sheets_model)
        self.sheetsList.contextMenuEvent = self._open_sheet_context_menu

        # set custom display options
        class ItemDelegate(QStyledItemDelegate):  # one time use class
            def paint(self, painter, option, index):
                option.decorationPosition = QStyleOptionViewItem.Right
                option.decorationAlignment = Qt.AlignLeading | Qt.AlignVCenter
                super().paint(painter, option, index)

        self.sheetsList.setItemDelegate(ItemDelegate())

    def _setup_campaign_list(self):
        self.campaignList.setModel(self.model.campaigns_model)
        self.campaignList.contextMenuEvent = self._open_campaign_context_menu

    def _setup_translation_table(self):
        """
        Sets up translation table in gui to display target columns and
        allow user to manipulate settings
        :return: None
        """
        self.assocTable.setModel(self.model.assoc_table_model)
        # resize headers depending on stored content
        header = self.assocTable.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.assocTable.setColumnWidth(1, 140)
        self.assocTable.setColumnWidth(2, 140)

    # Context menus

    def _open_sheet_context_menu(self, event):
        """
        Method called when user opens the context menu for an open
        sheet item.
        :return: None
        """
        # if list is empty, do nothing
        if self.sheetsList.model().is_empty:
            return
        if len(self.sheetsList.selectedIndexes()) == 0:
            return  # if user has managed to click the list,
            # but not an item in it, exit.
            # This is possible if they click very near the edge
        menu = QMenu(self)
        index = self.sheetsList.selectedIndexes()[0]  # get selected sheet i
        sheet = self.controller.sheet_from_index(index)

        # set src action
        if sheet is not self.model.source_sheet:
            set_src_action = menu.addAction("Select as source")
            set_src_action.triggered.connect(
                lambda: setattr(self.controller, 'src_sheet_i', index)
            )
        # remove src action
        else:
            clear_src_action = menu.addAction("Remove as source")
            clear_src_action.triggered.connect(
                lambda: setattr(self.controller, 'src_sheet_i', None)
            )
        # set tgt action
        if sheet is not self.model.target_sheet:
            set_tgt_action = menu.addAction("Select as target")
            set_tgt_action.triggered.connect(
                lambda: setattr(self.controller, 'tgt_sheet_i', index)
            )
        # remove tgt action
        else:
            clear_tgt_action = menu.addAction("Remove as target")
            clear_tgt_action.triggered.connect(
                lambda: setattr(self.controller, 'tgt_sheet_i', None)
            )
        menu.popup(QtGui.QCursor.pos())

    def _open_campaign_context_menu(self, event):
        """
        Method called when user opens the context (right click menu)
        of a campaign item in the campaigns list.
        :param event:
        :return: None
        """

        menu = QMenu(self)

        new_campaign_action = menu.addAction('New Campaign')
        new_campaign_action.triggered.connect(self.show_make_campaign_dlg)

        if len(self.campaignList.selectedIndexes()) > 0 and \
                not self.campaignList.model().is_empty:
            index = self.campaignList.selectedIndexes()[0]  # get selected i
            campaign = self.controller.campaign_from_index(index)

            del_campaign_action = menu.addAction(
                'Delete {}'.format(campaign.name)
            )
            del_campaign_action.triggered.connect(
                lambda: self.show_del_campaign_dlg(campaign)
            )

        menu.popup(QtGui.QCursor.pos())  # show context menu

    # Methods called from controller

    def confirm_tgt_overwrite(self) -> bool:
        reply = QMessageBox.question(
            self._dialog_parent,
            'Overwrite Cells?',
            'Cells on the target sheet will be overwritten.\n'
            'Proceed?',
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        return reply == QMessageBox.Yes

    def whitespace_feedback(self, whitespace_positions: tuple or list):
        """
        Reports to user on whitespace removals.
        :param whitespace_positions:
        """
        if not whitespace_positions:
            return
        print('giving whitespace feedback')
        info_string = ''
        if self.model.whitespace_action == WHITESPACE_REMOVE_STR:
            info_string = (
                'Cell values were edited to remove '
                'unneeded tab, linefeed, return, formfeed, '
                'and/or vertical tab characters.')
        elif self.model.whitespace_action == WHITESPACE_HIGHLIGHT_STR:
            info_string = (
                '%s Cell values were highlighted in '
                'checked '
                'columns' % len(whitespace_positions))
        self.show_info_dlg(
            title='Whitespace Found',
            main='Whitespace found in %s cells' % len(
                whitespace_positions),
            info=info_string,
            detail=self._position_report(*whitespace_positions)
        )

    def duplicates_feedback(self, duplicate_positions: tuple or list) -> None:
        """
        Provides feedback to user about duplicates and actions taken
        regarding said duplicates.
        :param duplicate_positions: iterable of duplicate_positions
        """
        if not duplicate_positions or \
                self.duplicate_action == DUPLICATE_IGNORE_STR:
            return
        print('giving duplicates feedback')
        info_string = ''
        if self.duplicate_action == DUPLICATE_HIGHLIGHT_STR:
            info_string = '%s Cell values were highlighted in ' \
                               'checked columns' % len(duplicate_positions)
        elif self.duplicate_action == DUPLICATE_REMOVE_ROW_STR:
            n_rows_w_duplicates = len(set(
                [pos[1] for pos in duplicate_positions]))
            info_string = '%s Cell rows containing duplicate ' \
                               'values were removed' % n_rows_w_duplicates
        self.show_info_dlg(
            title='Duplicate Values',
            main='%s Duplicate cell values found' % len(duplicate_positions),
            info=info_string,
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
            column_name = self.model.source_sheet.get_column(x).name
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

    # dialog display records

    def show_record_search_dlg(self):
        """
        Builds and shows record search dialog.
        :return: None
        """
        RecordValSearchDlg(self, self.model).exec()

    def show_records_view_dlg(self):
        """
        Builds and shows records view dialog.
        :return: None
        """
        RecordsViewDlg(self, self.model).exec()

    def show_make_campaign_query_dlg(self):
        """
        Shows user a query informing them that no campaigns currently
        exist and asking them if they wish to create one now.
        :return: None
        """
        title = 'Create Campaign?'
        main = 'No campaigns currently exist. Would you like to create '  \
               'one now?'
        info = 'Campaigns store settings and preferences, so that ' \
               'settings from previous translations can be auto-completed, ' \
               'and records can be grouped'
        dlg = QMessageBox(QMessageBox.Question, title, main)
        dlg.setInformativeText(info)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setStyleSheet(self.styleSheet())
        result = dlg.exec()
        if result == QMessageBox.Yes:
            self.show_make_campaign_dlg()

    def show_make_campaign_dlg(self):
        name = NewCampaignDlg(self, self.model).exec()
        if name:
            self.controller.new_campaign(name)

    def show_del_campaign_dlg(self, campaign):
        dlg = DelCampaignDlg(self.controller, self, campaign)
        dlg.setStyleSheet(self.styleSheet())
        if not dlg.exec():
            return
        elif dlg.confirmed:
            self.controller.del_campaign(campaign)

    # generic dialogs

    def show_info_dlg(self, title, main, info=None, detail=None):
        msg = QMessageBox(QMessageBox.Information, title, main)
        msg.setStyleSheet(self.styleSheet())
        msg.setInformativeText(info) if info else None
        msg.setDetailedText(detail) if detail else None
        msg.exec()

    def show_exception(self, e, title=None, main=None, info=None, detail=None):
        title = title if title else 'Exception'
        main = main if main else 'An exception occurred'
        msg = QMessageBox(QMessageBox.Information, title, main)
        msg.setStyleSheet(self.styleSheet())
        msg.setInformativeText(info if info else str(e))
        msg.setDetailedText(detail) if detail else None
        msg.exec()
