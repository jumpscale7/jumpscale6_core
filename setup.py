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

version = get_version('lib/JumpScale')

setup(name='JumpScale-core',
      version=version,
      description='Python Automation framework',
      author='JumpScale',
      author_email='info@jumpscale.org',
      url='http://www.jumpscale.org',

      packages = find_packages('lib'),
      package_dir = {'':'lib'},
      scripts=scripts,

      download_url='http://pypi.python.org/pypi/JumpScale/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: FreeBSD Software License',
    ]
)


if __name__ == '__main__':
    if sys.argv[-1] == 'publish':
        os.system("python setup.py sdist upload")
        print("You probably want to also tag the version now:")
        print("  hg tag -a %s -m 'version %s'" % (version, version))
        print("  hg push --tags")
        sys.exit()
