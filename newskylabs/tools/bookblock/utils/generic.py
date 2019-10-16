"""newskylabs/tools/bookblock/utils/generic.py

Various generic utilities...

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/16"

import os, sys, re
from os.path import join, dirname, isfile
import pathlib

## =========================================================
## Setup tools
## ---------------------------------------------------------

def get_version():
    """Return package version as defined in `setup.py` (ex: 1.2.3)."""

    package_base_dir = get_package_base_dir()
    
    main_file = os.path.join(package_base_dir, 'bookblock/__main__.py')
    init_py = open(main_file).read()
    match = re.search("__version__\s*=\s*['\"]([^'\"]+)['\"]", init_py)
    if match:
        version = match.group(1)
        return version
    else:
        raise RuntimeError("Unable to find version string in %s." % main_file)

def get_version_long():
    """Return long package version (ex: 1.2.3 (Python 3.4.5))."""

    return '{} (Python {})'.format(get_version(), sys.version[:5])

## =========================================================
## Tools for files and directories
## ---------------------------------------------------------

def get_package_base_dir():
    """Get the base dir of the package by searching the directory tree
    upward till a directory without '__init__.py' has been found.

    """
    directory = dirname(__file__);
    while isfile(join(directory, '__init__.py')):
        directory = dirname(directory)

    return directory

## =========================================================
## =========================================================

## fin.
