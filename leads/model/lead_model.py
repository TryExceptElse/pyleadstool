"""
Module storing model of leads information, including campaigns,
sources, etc
"""
import os

from .display_models import CampaignListModel, SheetListModel, \
    TranslationTableModel
from .campaign import CampaignCollection, \
    SETTINGS_WHITESPACE_KEY, SETTINGS_DUP_KEY
from .records import RecordCollection
from leadmacro import Office
from settings import APP_DATA_DIR, DB_FILE_PATH, CAMPAIGNS_PATH

TRANSLATION_TABLE_NAME = 'Translation'


class ModelException(Exception):
    """
    Signifies an exception getting or otherwise manipulating data
    in model.
    """


class Model:
    """
    model of leads information, including campaigns, sources, etc
    """

    def __init__(self, path: str=APP_DATA_DIR):
        try:
            self.office_model = Office.get_model()
        except ValueError:
            self.office_model = None
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)  # create dir if it does not already exist
        self.campaigns = CampaignCollection(CAMPAIGNS_PATH)
        self.records = RecordCollection(DB_FILE_PATH)
        self.campaign = None  # currently selected campaign
        self.source_sheet = None  # currently selected src
        self.target_sheet = None  # currently selected tgt
        self.source_sheet_start = None
        self.target_sheet_start = None
        self.assoc_table_model = TranslationTableModel(self)
        self.sheets_model = SheetListModel(self.office_model)
        self.campaigns_model = CampaignListModel(self)

    @property
    def whitespace_action(self):
        if self.campaign is None:
            raise ModelException('No campaign has been set')
        return self.campaign.settings[SETTINGS_WHITESPACE_KEY]

    @property
    def duplicate_action(self):
        if self.campaign is None:
            raise ModelException('No campaign has been set')
        return self.campaign.settings[SETTINGS_DUP_KEY]
