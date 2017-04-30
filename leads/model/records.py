"""
This module stores translation records, which store information about
when leads information has been moved, and what took place.
"""

import unqlite


class RecordCollection:
    """
    This class handles usage of the Translation Event collection in the db
    """

    def __init__(self, path: str):
        self.path = path
        self.db = unqlite.UnQLite(self.path)

    def add(self, translation: TranslationRecord) -> None:
        self.db[]


class TranslationRecord:
    """
    This class stores information about a single translation event,
    wherein information was moved from a source lead file to a target.
    """
