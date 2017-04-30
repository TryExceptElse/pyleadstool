"""
Imports
"""
from threading import Thread
from time import sleep
from PyQt5.Qt import QStandardItemModel, QStandardItem

from leadmacro import Model


UPDATE_CHECK_RATE = 15  # Hz


class SheetListModel(QStandardItemModel):
    """
    Model to be used by the SheetList on the main window,
    displaying alphabetical list of currently open sheets in Office.
    """
    def __init__(self, parent, office_model):
        super().__init__(parent)
        self.office_model = office_model
        self.sheet_names = set()
        self._connected = None

        self.update()
        # start watcher thread
        self.update_thread = Thread(
            target=self.watch_for_updates, daemon=True
        )
        self.update_thread.start()

    def clear(self):
        super().clear()
        self.sheet_names.clear()

    def watch_for_updates(self):
        while True:
            sleep(60 / UPDATE_CHECK_RATE)
            self.update()

    def update(self):
        if self.office_model is not None:
            # this will clear items, so it must be set first.
            self._has_connection = True
            assert isinstance(self.office_model, Model)
            for sheet_name in self.office_model.sheet_names:
                self.sheet_names.add(sheet_name)
                self.appendRow(self.SheetItem(sheet_name))
            self.sort(1)  # todo
        else:
            # if no way to connect to an office instance can be found,
            # office_model will be None
            self._has_connection = False

    @property
    def _has_connection(self):
        return self._connected

    @_has_connection.setter
    def _has_connection(self, connected: bool):
        if connected and not self._connected:
            self.clear()
        elif not connected and self._connected is not False:
            self.clear()
            self.appendRow(self.NoConnectionItem())

    class SheetItem(QStandardItem):
        """
        Individual item in sheet list model.
        """
        def __init__(self, sheet_name: str):
            super().__init__(sheet_name)
            self.sheet_name = sheet_name
            self.setText(sheet_name)

    class NoConnectionItem(QStandardItem):
        """
        This item displays a message to the user that no office
        connection could be found
        """
        def __init__(self):
            super().__init__()
            self.setText('No connection')
