## =========================================================
## Copyright 2019 Dietrich Bollmann
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##      http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## ---------------------------------------------------------

"""setup.py:

Setup file of the nsl-bookblock tool.

"""

import setuptools 
import codecs
import os

## =========================================================
## Setup utilities
## ---------------------------------------------------------

def read_file(*parts):
    """
    Read a file and return its content
    """
    package_dir = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(package_dir, *parts), 'r') as fp:
        return fp.read()

def find_packages(namespace, subnamespace):
    """Return a list of all Python packages defined in the 'namespace'
    directory.  A directory is only interpreted as a package if it
    contains a __init__.py file.

    """
    packages = [
        '{}.{}.{}'.format(namespace, subnamespace, package)
        for package in setuptools.PackageFinder.find(
                where='{}/{}'.format(namespace, subnamespace)
        )
    ]
    
    # DEBUG
    print("DEBUG packages:")
    for package in packages:
        print("  - {}".format(package))

    return packages

## =========================================================
## Setup
## ---------------------------------------------------------

# Namespace
namespace       = 'newskylabs'
subnamespace    = 'tools'
subsubnamespace = 'bookblock'

# Load the package metadata 
exec(read_file(namespace, subnamespace, subsubnamespace, '__about__.py'))

# Read the long description
long_description = read_file('README.md')

# Find the list of packages
packages = find_packages(namespace, subnamespace)

# Setup package
setuptools.setup(
    name=__package_name__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__email__,
    license=__license__,
    url=__url__,
    entry_points={
        'console_scripts': [
            'nsl-bookblock = newskylabs.tools.bookblock.__main__:bookblock',
        ]
    },
    keywords='deep learning, dataset generation, scan postprocessing, bookblock.',
    platforms=['Posix', 'Unix', 'Linux', 'MacOS X', 'Windows'],
    packages=packages,
    package_data={
        'newskylabs.tools.bookblock': [
            'data/scans/scan000.txt',
            'data/scans/*.txt'
        ]
    },
    include_package_data=True,
    install_requires=[
        'click>=7.0',
        'numpy>=1.17.2',
        # 'cv2>=4.1.1', # Install manually
        # 'pygame>=1.9.6', # Install manually
        # 'kivy>=1.11.1', # Install manually
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'Operating System :: OS Independent',
    ],
)

## =========================================================
## =========================================================

## fin.
