"""

"""
from threading import Thread
from time import sleep
from PyQt5.Qt import QStandardItemModel, QStandardItem

from leadmacro import Model


UPDATE_CHECK_RATE = 1  # Hz


class UpdatingListModel(QStandardItemModel):
    """
    List model which can be extended to create a regularly updating
    """
    update_frq = 1  # Hz

    def __init__(self, parent):
        super().__init__(parent)
        self.current_items = set()
        self.update()
        # start watcher thread
        self.update_thread = Thread(
            target=self.watch_for_updates, daemon=True
        )
        self.update_thread.start()

    def watch_for_updates(self):
        """
        Method that regularly updates the model
        :return: None
        """
        while True:
            sleep(60 / UPDATE_CHECK_RATE)
            self.update()

    def item_getter(self):
        """
        Method that finds and returns a collection of items
        to be used in model.
        Must be overridden in subclasses.
        For best performance, should return a set.
        :return:
        """
        raise NotImplementedError

    def factory(self, item):
        """
        Method that takes a item returned by getter and produces an
        instance of a class extending QStandardItem.
        Must be overridden by subclasses.
        :return: ? extending QStandardItem
        """
        raise NotImplementedError

    def update(self) -> None:
        """
        Updates model with new items and removes old ones.
        :return: None
        """
        new_item_set = set(self.item_getter())
        if len(new_item_set) == 0:
            # if set is empty, place marker for user
            self.clear()
            self.appendRow(self.EmptyListMarkerItem())
        # add each item in new items that is not in current_items
        for model_item in self.children():
            assert isinstance(model_item, self.UpdatingModelItem)
            if model_item.item not in new_item_set:
                self.removeRow(model_item)
        # remove each item in current items that is not in new items
        for item in self.current_items:
            if item not in new_item_set:
                self.appendRow(self.factory(item))

    class UpdatingModelItem(QStandardItem):
        def __init__(self, item):
            super().__init__()
            self.item = item

    class EmptyListMarkerItem(QStandardItem):
        """
        This item displays a message to the user that no items could
        be found.
        """
        def __init__(self):
            super().__init__()
            self.setText('No Items')


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
            sheets_in_model = set(self.office_model.sheet_names)
            # remove old sheet items
            for row in self.children():
                assert isinstance(row, self.SheetItem)
                if row.sheet_name not in sheets_in_model:
                    self.removeRow(row.index())
            # add new sheet items
            for sheet_name in sheets_in_model:
                if sheet_name not in self.sheet_names:
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


class CampaignListModel(UpdatingListModel):
    def __init__(self, parent, collection):
        self.collection = collection
        super().__init__(parent)

    def item_getter(self):
        return self.collection.campaigns

    def factory(self, item):
        return self.CampaignItem(item)

    class CampaignItem(UpdatingListModel.UpdatingModelItem):
        def __init__(self, campaign):
            super().__init__(campaign)
            self.setText(campaign.name)
