from unittest import TestCase

from leads.model.translation import _TranslationData, Validator


class TestTranslationData(TestCase):

    def test_translation_data_can_store_and_retrieve_validator_data(self):
        data = _TranslationData()
        validator = Validator()
        container = set()
        data.add_collection(validator, container)

        self.assertIs(container, data[validator])
