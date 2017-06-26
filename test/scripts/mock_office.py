from leads.model.sheets import Office as OfficeModel, Sheet


class MockColumns:
    names = None


class MockSheet:

    col_names = None

    def __init__(self):
        self.columns = MockColumns()


class MockOffice(OfficeModel):
    """
    Class mocking functionality of Office, for consistent testing
    regardless of presence of an office program to interact with.
    """

    has_connection = True

    mock_sheet_a = MockSheet()

    mock_sheet_b = MockSheet()

    mock_sheet_c = MockSheet()

    sheets = {
        'mock_sheet_a': mock_sheet_a,
        'mock_sheet_b': mock_sheet_b,
        'mock_sheet_c': mock_sheet_c,
    }

    sheet_names = sheets.keys()

    def __getitem__(self, item):
        return self.sheets[item]

