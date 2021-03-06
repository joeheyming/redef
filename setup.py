#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='redef',
      version='1.7',
      url='http://github.com/joeheyming/redef',
      maintainer_email='joeheyming@gmail.com',
      maintainer='Joseph Heyming',
      description='Test utility for redefining functions',
      download_url='https://github.com/joeheyming/redef/zipball/master',
      license='GNU GPLv3, Python License',
      long_description=open('README.md').read().replace('`',''),
      platforms = 'any',
      py_modules = ['redef'],
      # package_dir =  {'': 'lib'},
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'
    ]

      )
