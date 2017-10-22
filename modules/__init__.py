def import_all():
    from glob import glob
    from os import sep
    for f in glob('*/*/*.py'):
        name = f.replace(sep, '.')[:-3]
        if name.endswith('_') or name.endswith(sep+'module.py'):
            continue
        __import__(name)

import_all()