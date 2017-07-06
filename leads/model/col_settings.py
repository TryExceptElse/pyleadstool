"""
Module storing information about settings used for various previously
used columns.
"""


class ColSettings:
    """Class storing settings for a single column"""
    def __init__(self, name: str):
        self.name = name
        self.settings = {}
