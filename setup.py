from distutils.core import setup

import py2exe, PyQt5, xlwings

setup(
    name='LeadsTool',
    description='python leads utility',
    console=['leadmacro.py'],
    version='1.0',
    requires=['xlwings', 'PyQt5'],
    options={
        'py2exe': {
            'packages': ['xlwings', 'PyQt5']
        }
    }
)
