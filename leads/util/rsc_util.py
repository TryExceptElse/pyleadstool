"""
Holds various utility functions for using resources
"""
import os

import settings


def get_icon_path(*path_elements):
    return os.path.join(settings.RESOURCE_PATH, *path_elements)