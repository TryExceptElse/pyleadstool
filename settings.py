import os
import appdirs

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
UI_INPUT_DIR = os.path.join(PROJECT_ROOT, 'ui')
UI_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'leads', 'ui', 'layout')
APP_DATA_DIR = appdirs.user_data_dir('leads_tool')
DB_FILE_PATH = os.path.join(APP_DATA_DIR, 'db')
CAMPAIGNS_PATH = os.path.join(APP_DATA_DIR, 'campaigns')
