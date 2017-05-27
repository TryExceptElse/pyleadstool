"""
Module holding class representing a leads campaign, storing settings,
associations, records of previous translations, and other information.
"""
import os
import json

CAMPAIGN_NAME_KEY = 'name'
CAMPAIGN_SETTINGS_KEY = 'settings'
CAMPAIGN_FILE_EXT = '.json'

SETTINGS_WHITESPACE_KEY = 'whitespace_action'
SETTINGS_DUP_KEY = 'duplicate_action'


class CampaignCollection:
    """
    Obj that accesses, manipulates and parses information stored in
    the db campaigns collection
    """

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            os.mkdir(path)

    def __iter__(self):
        return self.campaigns

    @property
    def campaigns(self):
        # find each file in path that has appropriate ending
        for file_name in os.listdir(self.path):
            if not file_name.endswith(CAMPAIGN_FILE_EXT):
                continue
            with open(os.path.join(self.path, file_name)) as f:
                yield Campaign.from_file(f)


class Campaign:
    """
    Object handling a specific campaign entry in db
    """
    def __init__(self, name, settings=None):
        self.name = name
        self.settings = settings if settings else {}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d[CAMPAIGN_NAME_KEY], d[CAMPAIGN_SETTINGS_KEY])

    @classmethod
    def from_json(cls, s: str):
        return cls.from_dict(json.loads(s))

    @classmethod
    def from_file(cls, f) -> 'Campaign':
        return cls.from_dict(json.load(f))

    @property
    def as_dict(self):
        """
        Converts Campaign into a dictionary capable of being stored in
        a JSON file.
        :return: dict
        """
        return {
            CAMPAIGN_NAME_KEY: self.name,
            CAMPAIGN_SETTINGS_KEY: self.settings
        }

    @property
    def as_json(self):
        return json.dumps(self.as_dict)

    def to_file(self, f) -> None:
        json.dump(self.as_dict, f)
