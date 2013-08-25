#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

packages = [ 'JumpScale.portal' ]
packages += [ "JumpScale.portal.%s" % x for x in find_packages('portallib') ]

setup(name='JumpScale Portal',
      version='6.0.0',
      description='Python Automation framework',
      author='JumpScale',
      author_email='info@jumpscale.org',
      url='http://www.jumpscale.org',

      packages=packages,
      package_dir = {'JumpScale.portal': 'portallib'},

      download_url='http://pypi.python.org/pypi/JumpScale/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

