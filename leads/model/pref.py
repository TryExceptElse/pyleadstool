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
        except FileNotFoundError:
            pass  # if file is unreadable, just use empty settings dict

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

    # Getters and Setters


def restrict_inputs(*valid_inputs: object):
    valid_input_set = set(valid_inputs)

    def decorator(f):
        def wrapper(self, arg):
            if arg not in valid_input_set:
                raise ValueError(
                    f'{f.__name__} given invalid input: {arg}, valid inputs'
                    f'are: {valid_inputs}'
                )
            return f(self, arg)

        wrapper.__name__ = f.__name__ + '_wrapper'
        return wrapper

    return decorator


class CampaignPreferences(Preferences):

    WHITESPACE_ACTION = 'whitespace_action'
    DUPLICATE_ACTION = 'duplicate_action'

    REMOVE = 'remove'
    HIGHLIGHT = 'highlight'
    IGNORE = 'ignore'

    @property
    def whitespace_action(self) -> str:
        return self.d[self.WHITESPACE_ACTION]

    @whitespace_action.setter
    @restrict_inputs(REMOVE, HIGHLIGHT, IGNORE)
    def whitespace_action(self, new_setting: str):
        self.d[self.WHITESPACE_ACTION] = new_setting

    @property
    def duplicate_action(self) -> str:
        return self.d[self.DUPLICATE_ACTION]

    @duplicate_action.setter
    @restrict_inputs(REMOVE, HIGHLIGHT, IGNORE)
    def duplicate_action(self, new_setting: str):
        self.d[self.DUPLICATE_ACTION] = new_setting
