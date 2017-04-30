"""
Module holding class representing a leads campaign, storing settings,
associations, records of previous translations, and other information.
"""
import os


class CampaignCollection:
    """
    Obj that accesses, manipulates and parses information stored in
    the db campaigns collection
    """

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            os.mkdir(path)


class Campaign:
    """
    Object handling a specific campaign entry in db
    """
    def __init__(self, name, settings=None):
        self.name = name
        self.settings = settings if settings else {}

    def __dict__(self):
        """
        Converts Campaign into a dictionary capable of being stored in
        a JSON file.
        :return: dict
        """
        return {
            'name': self.name,
            'settings': self.settings
        }

    @staticmethod
    def json_hook(obj):
        if '__type__' in obj and obj['__type__'] == 'Campaign':
            return Campaign(obj['name'], obj['settings'])
        return obj
