"""
Module containing the main window
"""
from PyQt5.Qt import QMainWindow

from ..model.lead_model import Model
from .layout.mainwindow import Ui_MainWindow


class MainWin(QMainWindow, Ui_MainWindow):
    """
    Main window class
    """

    def __init__(self, model: Model):
        super().__init__()
        self.setupUi(self)  # apply layout to this main window

        self.model = model
        self.show()  # display main window to user

