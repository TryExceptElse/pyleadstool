"""
Module containing the main window.
This class also serves as the view of the program.
"""
from PyQt5.Qt import *  # all objects in package are named as QWidget, etc

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from .dialogs import RecordValSearchDlg, RecordsViewDlg
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

    def _setup_tool_bar(self):
        self.actionApplyTranslations.triggered.connect(self.controller.apply)
        self.actionCheck.triggered.connect(self.controller.check)
        self.searchAction.triggered.connect(self.controller.search_records)
        self.viewRecordsAction.triggered.connect(self.controller.view_records)

    def _setup_sheet_list(self):
        self.sheetsList.setModel(self.model.sheets_model)
        self.sheetsList.contextMenuEvent = self._open_sheet_context_menu

    def _setup_campaign_list(self):
        self.campaignList.setModel(self.model.campaigns_model)

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
        menu = QMenu(self)
        set_src_action = menu.addAction("Set as Source")
        set_tgt_action = menu.addAction("Set as Target")
        set_src_action.triggered.connect(
            lambda: self.controller.set_src_sheet_i(self._sheet_index(event))
        )
        set_tgt_action.triggered.connect(
            lambda: self.controller.set_tgt_sheet_i(self._sheet_index(event))
        )
        menu.popup(QtGui.QCursor.pos())

    def _sheet_index(self, event):
        return self.sheetsList.indexAt(event.pos())

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
        dlg = RecordValSearchDlg(self, self.model)
        dlg.exec()

    def show_records_view_dlg(self):
        """
        Builds and shows records view dialog.
        :return: None
        """
        dlg = RecordsViewDlg(self, self.model)
        dlg.exec()

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
