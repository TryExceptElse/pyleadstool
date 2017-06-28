"""
Holds various utility functions for using resources
"""
import os

import settings


def get_resource(*path_elements):
    return os.path.join(settings.RESOURCE_PATH, *path_elements)
