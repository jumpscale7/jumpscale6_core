#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import os
import glob
import sys

scripts = glob.glob('shellcmds/*')

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('lib/JumpScale')



def list_files(basedir='.', subdir='.'):
    package_data = []
    basedir_length = len(basedir)
    for dirpath, dirs, files in os.walk(os.path.join(basedir,subdir)):
        for file in files:
            package_data.append(os.path.join(dirpath[basedir_length+1:],file))
    return package_data
            

setup(name='JumpScale-core',
      version=version,
      description='Python Automation framework',
      author='JumpScale',
      author_email='info@jumpscale.org',
      url='http://www.jumpscale.org',
      license='FreeBSD',
      packages = find_packages('lib'),
      package_dir = {'':'lib'},
      include_package_data = True,
      package_data = {'JumpScale':list_files(basedir='lib/JumpScale','core/_defaultcontent')},
      scripts=scripts,

      download_url='http://pypi.python.org/pypi/JumpScale/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ]
)
