from .model.lead_model import Model
from .ui.main_win import MainWin
from .model.translation import Translation, ColumnTranslation
from .model.display_models import TranslationTableModel


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

    def record_translation(self, translation):
        try:
            self.model.records.add(translation)
        except Exception as e:
            self.view.show_exception(e, main='Could not record translation')

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
