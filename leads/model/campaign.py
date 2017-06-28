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

    def __delitem__(self, campaign: 'Campaign' or str):
        try:
            name = campaign.name
        except AttributeError:
            name = campaign
        path = os.path.join(self.path, name) + CAMPAIGN_FILE_EXT
        try:
            os.remove(path)
        except IOError or FileNotFoundError:
            pass

    @property
    def is_empty(self):
        """
        Gets whether or not collection is empty.
        :return: bool
        """
        return not len([f for f in os.listdir(self.path) if
                        f.endswith(CAMPAIGN_FILE_EXT)]) > 0

    def add_campaign(self, campaign: 'Campaign'):
        """
        Adds campaign to this collection.
        :return: None
        """
        # saves campaign into this collection's directory and sets
        # campaign's dir path attr
        campaign.dir_path = self.path
        campaign.save()

    @property
    def campaigns(self):
        # find each file in path that has appropriate ending
        for file_name in os.listdir(self.path):
            if not file_name.endswith(CAMPAIGN_FILE_EXT):
                continue
            with open(os.path.join(self.path, file_name)) as f:
                campaign = Campaign.from_file(f)
                campaign.dir_path = self.path
                yield campaign


class Campaign:
    """
    Object handling a specific campaign entry in db
    """
    def __init__(self, name, dir_path=None, settings=None):
        self.name = name
        self.dir_path = dir_path
        self.settings = settings if settings else {}

    # save / load

    def save(self, dir_path=None):
        """
        Saves to previously set path
        :return: None
        """
        if dir_path is None:
            dir_path = self.dir_path
        if dir_path is None:  # if dir path is still None
            raise ValueError('No dir path has been set for Campaign and none'
                             'was passed to save method.')
        f_path = os.path.join(dir_path, self.name) + CAMPAIGN_FILE_EXT
        # save to path
        with open(f_path, 'w+') as f:
            self.to_file(f)

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
