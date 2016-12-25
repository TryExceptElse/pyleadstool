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

DFT_SRC = 'st_src_1'
DFT_TGT = 'st_tgt_1'


def test_translation_speed_is_improved(src_sheet=None, tgt_sheet=None):
    """
    Test speed at which a test translation is applied.
    :return: None
    """
    if src_sheet is None:
        src_sheet = DFT_SRC
    if tgt_sheet is None:
        tgt_sheet = DFT_TGT
    model = Office.get_model()
    print('getting sheets')
    sheet_finding_start_time = time()
    src_sheet = model[src_sheet]
    tgt_sheet = model[tgt_sheet]
    # enable caching, as should be the case in regular use
    src_sheet.exclusive_editor = True
    tgt_sheet.exclusive_editor = True
    print('finished getting sheet instances (%ss)' %
          (time() - sheet_finding_start_time))
    assert isinstance(src_sheet, Office.XW.Sheet), src_sheet
    assert isinstance(tgt_sheet, Office.XW.Sheet), tgt_sheet
    print('getting src col names')
    src_col_start_time = time()
    src_col_names = [name for name in src_sheet.columns.names]
    print('finished getting src col names (%ss)'
          % (time() - src_col_start_time ))
    print('getting tgt col names')
    tgt_col_start_time = time()
    tgt_col_names = [name for name in tgt_sheet.columns.names]
    print('finished getting src col names (%ss)'
          % (time() - tgt_col_start_time))
    shuffle(src_col_names)
    # make translation dicts
    translation_dicts = []
    i = 0
    n = len(src_col_names)
    assert len(src_col_names) == len(tgt_col_names)
    print('building translation')
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
    print('done building translation dictionaries')
    print('starting clock')
    start_time = time()
    print('building Translation')
    translation_build_t1 = time()
    translation = Translation(
        None,
        source_sheet=src_sheet,
        target_sheet=tgt_sheet,
        column_translations=translation_dicts,
    )
    print('finished building translation (%ss)'
          % (time() - translation_build_t1))
    print('committing translation')
    commit_t1 = time()
    translation.commit()
    print('finished commit. (%ss)' % (time() - commit_t1))
    elapsed_time = time() - start_time
    print('finished')
    print(
        '\nRUN TIME     : %s\n TIME TO BEAT : %s\n' %
        (elapsed_time, OVERALL_TIME_TO_BEAT)
    )


if __name__ == '__main__':

    if xw is None:
        assert False, "XW was unable to be imported"

    test_translation_speed_is_improved('st_src_short')
