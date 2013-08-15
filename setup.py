#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

packages = [ 'OpenWizzy.portal' ]
packages += [ "OpenWizzy.portal.%s" % x for x in find_packages('portallib') ]

setup(name='OpenWizzy Portal',
      version='6.0.0',
      description='Python Automation framework',
      author='OpenWizzy',
      author_email='info@openwizzy.org',
      url='http://www.openwizzy.org',

      packages=packages,
      package_dir = {'OpenWizzy.portal': 'portallib'},

      download_url='http://pypi.python.org/pypi/OpenWizzy/',
      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

