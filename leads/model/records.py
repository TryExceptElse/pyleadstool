"""
This module stores translation records, which store information about
when leads information has been moved, and what took place.
"""

import unqlite
import json
import uuid

from .translation import Translation, LOG_DATE_TIME_KEY, LOG_TGT_COLUMNS_KEY


UUID_KEY = 'uuid'


class RecordCollection:
    """
    This class handles usage of the Translation Event collection in the db
    """

    def __init__(self, path: str):
        self.path = path
        self.db = unqlite.UnQLite(self.path)

    def add(self, translation: 'Translation') -> None:
        """
        Adds a Translation instance into records.
        :param translation: Translation
        :return None
        """
        translation_record = TranslationRecord(translation)
        self.db[translation_record.key] = translation_record

    def values_set(self, key: str, min_datetime=None) -> set:
        values = set()
        for record in self:
            # check if date is in acceptable range
            if min_datetime is None or record.t > min_datetime:
                values.update(record.values_set(key))
        return values
        # todo: cache previously used sets in new db for quick access

    def __iter__(self):
        for k, record in self.db:
            yield TranslationRecord(record)


class TranslationRecord:
    """
    This class stores information about a single translation event,
    wherein information was moved from a source lead file to a target.
    """
    def __init__(self, arg, record_collection=None):
        if isinstance(arg, str):
            # parse json
            self._dict = json.loads(arg)
        elif isinstance(arg, Translation):
            # parse Translation into record
            self._dict = arg.as_dict
            if UUID_KEY not in self._dict:
                self._dict[UUID_KEY] = uuid.uuid4()
        else:
            raise ValueError(
                'TranslationRecord() was passed {}. A str or'
                'Translation object was expected.'
                .format(arg)
            )
        self.record_collection = record_collection  # set at creation time

    def values_set(self, key: str):
        entries = self._dict[LOG_TGT_COLUMNS_KEY]
        values = set()
        for entry in entries:
            try:
                values.add(entry[key])
            except KeyError:
                pass
        return values

    @property
    def as_json(self):
        return json.dumps(self._dict)

    @property
    def key(self):
        return self._dict[UUID_KEY]

    @property
    def t(self) -> str:
        return self._dict[LOG_DATE_TIME_KEY]
