"""
Module containing the main window.
This class also serves as the view of the program.
"""
from PyQt5.Qt import *  # all objects in package are named as QWidget, etc

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

    def _setup_sheet_list(self):
        self.sheetsList.setModel(self.model.sheets_model)

    def _setup_campaign_list(self):
        self.campaignList.setModel(self.model.campaigns_model)

    def _setup_translation_table(self):
        """
        Sets up translation table in gui to display target columns and
        allow user to manipulate settings
        :return: None
        """
        self.assocTable.setModel(self.model.assoc_table_model)

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

    @classmethod
    def show_info_dlg(cls, title, main, info, detail):
        msg = QMessageBox(QMessageBox.Information, title, main)
        msg.setInformativeText(info) if info else None
        msg.setDetailedText(detail) if detail else None
        msg.exec()

    @classmethod
    def show_exception(cls, e, title=None, main=None, info=None, detail=None):
        if title is None:
            title = 'Exception'
        if main is None:
            main = 'An exception occurred'
        msg = QMessageBox(QMessageBox.Information, title, main)
        msg.setInformativeText(info if info else str(e))
        msg.setDetailedText(detail) if detail else None
        msg.exec()
