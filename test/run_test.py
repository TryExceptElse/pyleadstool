import os

from cProfile import run

import settings

if __name__ == '__main__':
    out = os.path.join(settings.PROJECT_ROOT, 'out_test', 'run_profile.cprof')
    run('test_translation_speed_is_improved()', out)