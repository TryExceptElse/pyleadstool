"""
This module contains the script that launches a gui.
Unlike the lead macro, this does not have cross-platform compatibility.
"""
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QIcon

from leads.util import rsc_util
from leads.model.lead_model import Model
from leads.controller import Controller
from leads.ui.main_win import MainWin


def main():
    logging.basicConfig(
       level=logging.DEBUG,
       format='(%(threadName)-12s) % (message)s',
    )
    app = QApplication([''])  # expects list of strings.
    app.setWindowIcon(QIcon(rsc_util.get_resource('icon-64-arrow-right4')))
    model = Model()
    main_win = MainWin(model)
    controller = Controller(model, main_win)
    app.exec()


if __name__ == '__main__':
    main()
