"""
This is the command package for tree_depend
"""
import os

__all__ = []

def update_all():
    global __all__
    __all__.clear()
    # Get this __init__.py file's absolute path
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    # Load all *.py files into __all__ that are not __init__.py
    __all__ = [s[:-3] for s in os.listdir(DIR_PATH) \
                if ".py" in s and not (str(s).startswith("_") \
                or str(s).startswith("."))]
    # Load all directories into py_files that contain a __init__.py file
    __all__ += [s for s in os.listdir(DIR_PATH) \
                if os.path.isdir(os.path.join(DIR_PATH, s)) \
                and os.path.isfile(os.path.join(DIR_PATH, s, "__init__.py"))]

update_all()
