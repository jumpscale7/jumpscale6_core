#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import glob

from setuptools import setup, find_packages
from setuptools.command.install import install

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('lib/JumpScale')
scripts = glob.glob('shellcmds/*')

def list_files(basedir='.', subdir='.'):
    """
    Used by setup function to list some needed data files in specific directories
    """
    package_data = []
    basedir_length = len(basedir)
    for dirpath, _, files in os.walk(os.path.join(basedir,subdir)):
        for f in files:
            package_data.append(os.path.join(dirpath[basedir_length+1:],f))
    return package_data

class Clean(install):
    """cleans environment before installation"""
    
    def run(self):
        print "\n**CLEANING PREVIOUS JUMPSCALE INSTALLATIONS**\n"

        for r,_,f in os.walk("/usr"):
            for path in f:
                if path.startswith("jscode") or\
                        path.startswith("jpackage") or\
                        path.startswith("jspackage") or\
                        path.startswith("jsdevelop") or\
                        path.startswith("jsreinstall") or\
                        path.startswith("jsprocess") or\
                        path.startswith("jslog") or\
                        path.startswith("jsshell") or\
                        path.startswith("osis") or\
                        path.startswith("js"):
                    
                    os.remove(os.path.join(r,path))
                    print "removed:%s" % os.path.join(r,path)

        cmds=['rm -rf /usr/local/lib/python2.7/dist-packages/jumpscale/',
              'rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale_core-6.0.0.egg-info/',
              'killall tmux']

        for cmd in cmds:
            os.system("%s 2>&1 > /dev/null; echo" % cmd)
            if cmd.startswith('rm'):
                print "removed:%s" % cmd.split(' ')[-1]

        install.run(self)

setup(name='JumpScale-core',
      version=version,
      description='Python Automation framework',
      author='JumpScale',
      author_email='info@jumpscale.org',
      url='http://www.jumpscale.org',
      license='BSD 2-Clause',
      packages = find_packages('lib'),
      package_dir = {'':'lib'},
      include_package_data = True,
      package_data = {'JumpScale':list_files(basedir='lib/JumpScale',subdir='core/_defaultcontent') +
                                  list_files(basedir='lib/JumpScale',subdir='baselib/jpackages/templates')
                     },
      scripts=scripts,

      download_url='http://pypi.python.org/pypi/JumpScale/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ],
    cmdclass={'install': Clean}
)