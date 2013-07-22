#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import os
import glob

scripts = glob.glob('shellcmds/*')

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('lib/OpenWizzy')

setup(name='OpenWizzy',
      version=version,
      description='Python Automation framework',
      author='OpenWizzy',
      author_email='info@openwizzy.org',
      url='http://www.openwizzy.org',

      packages = find_packages('lib'),
      package_dir = {'':'lib'},
      scripts=scripts,

      download_url='http://pypi.python.org/pypi/OpenWizzy/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

