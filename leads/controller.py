import logging

from .model.campaign import Campaign
from .model.lead_model import Model
from .model.translation import Translation, ColumnTranslation, ValidationReport
from .model.display_models import TranslationTableModel
from .ui.main_win import MainWin


# pylint: disable=W0703
class Controller:
    def __init__(self, model: Model, view: MainWin):
        self.model = model
        self.view = view
        self.view.controller = self  # set view controller to self

    # user actions

    def apply(self):
        logger = logging.getLogger(__name__)
        logger.debug('creating & applying translation')
        try:
            translation = self._make_translation()
            self.check(translation)  # show detected whitespace + duplicates
            translation.commit()
        except Exception as e:
            self.view.show_exception(e, main='Could not apply translations')
        else:
            self.record_translation(translation)
            self.view.show_info_dlg(  # tell user translation has been applied
                title='Macro Finished',
                main='Finished moving cell values'
            )

    def check(self, translation: Translation=None):
        logger = logging.getLogger(__name__)
        logger.debug('checking for duplicates and whitespace')
        # make translation without committing, to be used to find
        # cells that will be used in translation that have whitespace
        # duplicates, or other features.
        try:
            if not translation:
                translation = self._make_translation()
            self.view.display_validation_report(translation.check())
        except Exception as e:
            self.view.show_exception(e, main='Could not check data.')

    def search_records(self):
        logger = logging.getLogger(__name__)
        logger.debug('showing record search dlg')
        try:
            # show search records dlg
            self.view.show_record_search_dlg()
        except Exception as e:
            logger.exception(
                'Exception occurred while showing record search dlg')
            self.view.show_exception(
                e, main='Could not show record search dialog.')

    def view_records(self):
        logger = logging.getLogger(__name__)
        logger.debug('showing record viewing dlg')
        try:
            # show record view dlg
            self.view.show_records_view_dlg()
        except Exception as e:
            logger.exception(
                'Exception occurred while showing record viewing dlg')
            self.view.show_exception(e, main='Could not view records.')

    def record_translation(self, translation):
        logger = logging.getLogger(__name__)
        logger.debug('recording translation')
        try:
            self.model.records.add(translation)
        except Exception as e:
            logger.exception('Exception occurred while recording translation')
            self.view.show_exception(e, main='Could not record translation')

    # context menu methods

    @property
    def tgt_sheet_i(self):
        """
        Gets index of tgt sheet for translation.
        If no target is set, returns None
        :return: QIndex
        """
        if self.model.target_sheet is None:
            return None
        else:
            return self._index_from_sheet(self.model.target_sheet)

    @tgt_sheet_i.setter
    def tgt_sheet_i(self, index):
        """
        Sets sheet to be the source for translation.
        :param index: QIndex
        :return: None
        """
        logger = logging.getLogger(__name__)
        logger.debug('setting target sheet from index: {}'.format(index))
        if self.model.target_sheet:  # if tgt was previously set, clear icon
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()

        # if tgt is being unset (passed None)...
        if index is None:
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()
            self.model.target_sheet = None
            self.model.assoc_table_model.update()
            return

        sheet = self.sheet_from_index(index)
        # if sheet was previously marked as the source, unset src sheet
        if sheet is self.model.source_sheet:
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()
            self.model.source_sheet = None
        self.model.target_sheet = sheet
        item = self._sheet_item_from_index(index)  # get sheet icon
        item.mark_as_tgt()
        self.model.assoc_table_model.update()

    @property
    def src_sheet_i(self):
        """
        Gets index of source sheet.
        :return: QModelIndex
        """
        if self.model.source_sheet is None:
            return None
        else:
            return self._index_from_sheet(self.model.source_sheet)

    @src_sheet_i.setter
    def src_sheet_i(self, index) -> None:
        """
        Sets sheet to be the target for translation.
        :param index: QModelIndex
        :return: None
        """
        logger = logging.getLogger(__name__)
        logger.debug('setting source sheet from index: {}'.format(index))
        if self.model.source_sheet:  # if src was previously set, clear icon
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()

        # if src is being unset...
        if index is None:
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()
            self.model.source_sheet = None
            self.model.assoc_table_model.update()  # update table
            return

        # otherwise, if a real index has been passed...
        sheet = self.sheet_from_index(index)
        if sheet is self.model.target_sheet:  # if sheet was previously the tgt
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()
            self.model.target_sheet = None  # clear it, as it can't be both
        self.model.source_sheet = sheet
        item = self._sheet_item_from_index(index)  # get sheet icon
        item.mark_as_src()
        # update translation table view
        self.model.assoc_table_model.update()

    def _index_from_sheet(self, goal_sheet):
        logger = logging.getLogger(__name__)
        logger.debug('finding index of sheet: {}'.format(goal_sheet))
        for r, sheet_item in enumerate(self.model.sheets_model):
            sheet = self.model.office_model[sheet_item.sheet_id]
            if sheet is goal_sheet:
                return self.model.sheets_model.index(r, 0)

    def _sheet_item_from_index(self, i):
        return self.model.sheets_model.itemFromIndex(i)

    def sheet_from_index(self, i):
        logger = logging.getLogger(__name__)
        logger.debug('finding sheet from index: {}'.format(i))
        sheet_item = self.model.sheets_model.itemFromIndex(i)
        sheet_id = sheet_item.sheet_id
        sheet = self.model.office_model[sheet_id]
        return sheet

    # campaign creation / edit / etc methods

    def new_campaign(self, name: str):
        logger = logging.getLogger(__name__)
        logger.debug('creating new campaign of name: {}'.format(name))
        campaign = Campaign(name)
        self.model.campaigns.add_campaign(campaign)
        campaign.save()
        self.model.campaign = campaign  # set new campaign as active campaign
        self.model.campaigns_model.update()  # update displayed campaigns list

    def del_campaign(self, campaign: 'Campaign'):
        logger = logging.getLogger(__name__)
        logger.debug('deleting campaign: {}'.format(campaign))
        del self.model.campaigns[campaign.name]
        self.model.campaigns_model.update()

    @property
    def active_campaign_i(self):
        """
        Gets index of active campaign.
        Not particularly efficient.
        :return: QModelIndex
        """
        campaign = self.model.campaign
        if campaign is None:
            return None
        else:
            return self.model.campaigns_model.index_from_element(campaign)

    @active_campaign_i.setter
    def active_campaign_i(self, index):
        logger = logging.getLogger(__name__)
        logger.debug('setting active campaign from index: {}'.format(index))
        campaigns_model = self.model.campaigns_model

        # clear previous mark if one exists
        if self.active_campaign_i:
            current_index = self.active_campaign_i
            current_item = campaigns_model.itemFromIndex(current_index)
            current_item.clear_mark()

        # if campaign is being unset (index set to None)...
        if index is None:
            self.model.campaign = None
            return

        # otherwise
        campaign_list_item = campaigns_model.itemFromIndex(index)
        campaign_list_item.mark_as_current()
        self.model.campaign = campaign_list_item.item

    # update / utility methods

    def _make_translation(self) -> 'Translation':
        """
        Helper method creating a translation using information from the
        lead model.
        :return: Translation
        """
        logger = logging.getLogger(__name__)
        logger.debug('creating translation: src={}, tgt={}'
                     .format(self.model.source_sheet, self.model.target_sheet))
        # create translation obj
        translation = Translation(
            source_sheet=self.model.source_sheet,
            target_sheet=self.model.target_sheet,
            source_start_row=self.model.source_sheet_start,
            target_start_row=self.model.target_sheet_start,
            whitespace_action=self.model.whitespace_action,
            duplicate_action=self.model.duplicate_action,
            overwrite_confirm_func=self.view.confirm_tgt_overwrite,
            record_to_read=self.model.records
        )
        # add column translations
        for col_entry in self.model.assoc_table_model.translation_entries:
            assert isinstance(col_entry, TranslationTableModel.ColEntry)
            col_translation = ColumnTranslation(
                parent_translation=translation,
                source_column_i=col_entry.src_col.index
            )
            translation.add_column_translation(col_translation)
        return translation
