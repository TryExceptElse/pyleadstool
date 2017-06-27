"""
Module storing classes for storing user preferences, information
about program state, etc
"""
import json


class Preferences:
    def __init__(self, path: str):
        self.path = path
        self.d = {}
        try:
            self.load()
        except json.decoder.JSONDecodeError or IOError:
            pass  # if file is unreadable, just use empty settings dict

    def __getitem__(self, k):
        return self.d[k]

    def __setitem__(self, k, v):
        self.d[k] = v

    def __delitem__(self, k):
        del self.d[k]

    # File IO methods

    def save(self):
        with open(self.path, 'w+') as f:
            self.to_file(f)

    def to_file(self, f):
        json.dump(self.d, f)

    def load(self):
        with open(self.path, 'r+') as f:
            self.from_file(f)

    def from_file(self, f):
        self.d = json.load(f)
