"""
This module contains a script that builds all ui modules from qt layout
.ui files.

The input and output directories are identified
"""

import os
import subprocess

from settings import UI_OUTPUT_DIR, UI_INPUT_DIR


LAYOUT_FILE_ENDING = '.ui'
OUTPUT_FILE_ENDING = '.py'


def build_layout_directory(layout_dir: str, target_dir: str):
    # get each file name in layout dir
    for name in os.listdir(layout_dir):
        if not name.endswith(LAYOUT_FILE_ENDING):
            continue
        layout_src_path = os.path.join(layout_dir, name)
        layout_tgt_path = os.path.join(target_dir, _to_py_module_name(name))
        build_layout(layout_src_path, layout_tgt_path)


def build_layout(layout_file_path: str, target_path: str):
    if not layout_file_path.endswith(LAYOUT_FILE_ENDING):
        raise ValueError('file %s does not appear to be a layout file')
    with open(target_path, 'wb') as tgt_file:
        result = subprocess.run(
            ('pyuic5', layout_file_path),
            stdout=subprocess.PIPE
        )
        tgt_file.write(result.stdout)
    print('{} created from .ui file.'.format(os.path.basename(target_path)))


def _to_py_module_name(layout_name: str):
    if not layout_name.endswith(LAYOUT_FILE_ENDING):
        raise ValueError('file %s does not appear to be a layout file')
    return layout_name[:-len(LAYOUT_FILE_ENDING)] + OUTPUT_FILE_ENDING


if __name__ == '__main__':
    build_layout_directory(UI_INPUT_DIR, UI_OUTPUT_DIR)
