"""
This module contains the script that launches a gui.
Unlike the lead macro, this does not have cross-platform compatibility.
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QIcon

from leads.util import rsc_util
from leads.model.lead_model import Model
from leads.controller import Controller
from leads.ui.main_win import MainWin


if __name__ == '__main__':
    app = QApplication([''])  # expects list of strings.
    app.setWindowIcon(QIcon(rsc_util.get_icon_path('icon-64-arrow-right4')))
    model = Model()
    main_win = MainWin(model)
    controller = Controller(model, main_win)
    app.exec()
