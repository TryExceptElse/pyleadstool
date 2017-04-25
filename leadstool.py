"""
This module contains the script that launches a gui.
Unlike the lead macro, this does not have cross-platform compatibility.
"""
from PyQt5.QtWidgets import QApplication

from leads.model.lead_model import Model
from leads.ui.main_win import MainWin


if __name__ == '__main__':
    app = QApplication([''])  # expects list of strings.
    model = Model()
    main_win = MainWin(model)
    app.exec()
