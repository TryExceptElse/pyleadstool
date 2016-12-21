"""
Tests speed at which IO occurs, reading and writing values to the
Office program

Times:

"""

from leadmacro import Office, Translation

from time import time
from random import shuffle

try:
    import xlwings as xw
except ImportError:
    xw = None

OVERALL_TIME_TO_BEAT = None

SOURCE_COLUMN_NAME_KEY = 'source_column_name'
TARGET_COLUMN_NAME_KEY = 'target_column_name'
WHITESPACE_CHK_KEY = 'check_for_whitespace'
DUPLICATE_CHK_KEY = 'check_for_duplicates'

if __name__ == '__main__':
    model = Office.get_model()

    if xw is None:
        assert False, "XW was unable to be imported"


    def test_translation_speed_is_improved(self):
        """
        Test speed at which a test translation is applied.
        :return:
        """
        src_sheet = self.model.get_sheet('st_src_1')  # todo: make this sheet
        tgt_sheet = self.model.get_sheet('st_tgt_1')  # todo: make this sheet
        assert isinstance(src_sheet, Office.XW.Sheet)
        assert isinstance(tgt_sheet, Office.XW.Sheet)
        src_col_names = src_sheet.columns.names
        tgt_col_names = src_sheet.columns.names
        shuffle(src_col_names)
        # make translation dicts
        translation_dicts = []
        i = 0
        n = len(src_col_names)
        assert len(src_col_names) == len(tgt_col_names)
        for src_col_name, tgt_col_name in zip(src_col_names, tgt_col_names):
            # in first 1/5 of column transforms, check for duplicates
            if i <= n / 5:
                duplicate_chk = True
            else:
                duplicate_chk = False
            translation_dicts.append({
                SOURCE_COLUMN_NAME_KEY: src_col_name,
                TARGET_COLUMN_NAME_KEY: tgt_col_name,
                DUPLICATE_CHK_KEY: duplicate_chk,
                WHITESPACE_CHK_KEY: True
            })
        start_time = time()
        translation = Translation(
            None,
            source_sheet=src_sheet,
            target_sheet=tgt_sheet,
            column_translations=translation_dicts,
        )
        translation.commit()
        elapsed_time = time() - start_time
        print(
            '\nRUN TIME     : %s\n TIME TO BEAT : %s\n' %
            (elapsed_time, OVERALL_TIME_TO_BEAT)
        )
