from .model.campaign import Campaign
from .model.lead_model import Model
from .model.translation import Translation, ColumnTranslation
from .model.display_models import TranslationTableModel
from .ui.main_win import MainWin


class Controller:
    def __init__(self, model: Model, view: MainWin):
        self.model = model
        self.view = view
        self.view.controller = self  # set view controller to self

    # user actions

    def apply(self):
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

    def check(self, translation=None):
        # make translation without committing, to be used to find
        # cells that will be used in translation that have whitespace
        # duplicates, or other features.
        try:
            if not translation:
                translation = self._make_translation()
            duplicates = translation.get_duplicate_positions()
            self.view.duplicates_feedback(duplicates)
            whitespaces = translation.get_whitespace_positions()
            self.view.whitespace_feedback(whitespaces)
        except Exception as e:
            self.view.show_exception(e, main='Could not check data.')

    def search_records(self):
        try:
            # show search records dlg
            self.view.show_record_search_dlg()
        except Exception as e:
            self.view.show_exception(
                e, main='Could not show record search dialog.')

    def view_records(self):
        try:
            # show record view dlg
            self.view.show_records_view_dlg()
        except Exception as e:
            self.view.show_exception(e, main='Could not view records.')

    def record_translation(self, translation):
        try:
            self.model.records.add(translation)
        except Exception as e:
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
        # if tgt is being unset (passed None)...
        if index is None:
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()
            self.model.target_sheet = None
            return

        sheet = self.sheet_from_index(index)
        if self.model.target_sheet:  # if tgt was previously set, clear icon
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()
        # if sheet was previously marked as the source, unset src sheet
        if sheet is self.model.source_sheet:
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()
            self.model.source_sheet = None
        self.model.target_sheet = sheet
        item = self._sheet_item_from_index(index)  # get sheet icon
        item.mark_as_tgt()

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
        # if src is being unset...
        if index is None:
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()
            self.model.source_sheet = None
            return

        # otherwise, if a real index has been passed...
        sheet = self.sheet_from_index(index)
        if self.model.source_sheet:  # if src was previously set, clear icon
            self._sheet_item_from_index(self.src_sheet_i).clear_mark()
        if sheet is self.model.target_sheet:  # if sheet was previously the tgt
            self._sheet_item_from_index(self.tgt_sheet_i).clear_mark()
            self.model.target_sheet = None  # clear it, as it can't be both
        self.model.source_sheet = sheet
        item = self._sheet_item_from_index(index)  # get sheet icon
        item.mark_as_src()

    def _index_from_sheet(self, goal_sheet):
        for r, sheet_item in enumerate(self.model.sheets_model):
            sheet = self.model.office_model[sheet_item.sheet_id]
            if sheet is goal_sheet:
                return self.model.sheets_model.index(r, 0)

    def _sheet_item_from_index(self, i):
        return self.model.sheets_model.itemFromIndex(i)

    def sheet_from_index(self, i):
        sheet_item = self.model.sheets_model.itemFromIndex(i)
        sheet_id = sheet_item.sheet_id
        sheet = self.model.office_model[sheet_id]
        return sheet

    # campaign creation / edit / etc methods

    def new_campaign(self, name: str):
        campaign = Campaign(name)
        self.model.campaigns.add_campaign(campaign)
        campaign.save()
        self.model.campaign = campaign  # set new campaign as active campaign
        self.model.campaigns_model.update()  # update displayed campaigns list

    def del_campaign(self, campaign: 'Campaign'):
        del self.model.campaigns[campaign.name]
        self.model.campaigns_model.update()

    def campaign_from_index(self, index) -> 'Campaign':
        campaign_item = self.model.campaigns_model.itemFromIndex(index)
        campaign = campaign_item.item
        return campaign

    # update / utility methods

    def _make_translation(self) -> 'Translation':
        """
        Helper method creating a translation using information from the
        lead model.
        :return: Translation
        """
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
