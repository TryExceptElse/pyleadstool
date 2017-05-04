"""
Module storing model of leads information, including campaigns,
sources, etc
"""
import os

from .campaign import CampaignCollection, Campaign
from .records import RecordCollection
from leadmacro import Office
from settings import APP_DATA_DIR, DB_FILE_PATH, CAMPAIGNS_PATH

TRANSLATION_TABLE_NAME = 'Translation'


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
            os.mkdir(self.path)
        self.campaigns = CampaignCollection(CAMPAIGNS_PATH)
        self.records = RecordCollection(DB_FILE_PATH)
        self.campaign = None  # currently selected campaign
        self.source_sheet = None  # currently selected src
        self.target_sheet = None  # currently selected tgt
