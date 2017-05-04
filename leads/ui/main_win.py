"""
Module containing the main window
"""
from PyQt5.Qt import QMainWindow

from ..model.lead_model import Model
from .layout.mainwindow import Ui_MainWindow
from .data_model import SheetListModel


class MainWin(QMainWindow, Ui_MainWindow):
    """
    Main window class
    """

    def __init__(self, model: Model):
        super().__init__()
        self.setupUi(self)  # apply layout to this main window
        self.model = model
        self._complete_gui()

        self.show()  # display main window to user

    def _complete_gui(self):
        self._setup_sheet_list()

    def _setup_sheet_list(self):
        self.sheetsList.setModel(SheetListModel(
            self.sheetsList, self.model.office_model
        ))

    def _setup_campaign_list(self):
        self.campaignList.setModel()


