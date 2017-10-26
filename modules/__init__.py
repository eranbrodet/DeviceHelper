def import_all():
    from glob import glob
    from os import sep
    from os.path import join, split, relpath

    parent = split(__file__)[0]
    for f in glob(join(parent, '*/*.py')): #TODO can I import get_full_path here or is it circular
        name = relpath(f, parent).replace(sep, '.')[:-3]
        if name.endswith('_') or name.endswith(sep+'module.py'):
            continue
        __import__('modules.'+name)

import_all()