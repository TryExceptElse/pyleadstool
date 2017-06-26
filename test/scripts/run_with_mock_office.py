"""
Runs leadstool, but replaces office model with a mock office
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QIcon

from leads.util import rsc_util
from leads.model.lead_model import Model
from leads.model.display_models import SheetListModel
from leads.controller import Controller
from leads.ui.main_win import MainWin

from test.scripts.mock_office import MockOffice


if __name__ == '__main__':
    app = QApplication([''])  # expects list of strings.
    app.setWindowIcon(QIcon(rsc_util.get_icon_path('icon-64-arrow-right4')))
    mock_office_model = MockOffice()
    model = Model(office_model=mock_office_model)
    main_win = MainWin(model)
    controller = Controller(model, main_win)
    app.exec()
