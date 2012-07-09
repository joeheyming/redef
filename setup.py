#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='redef',
      version='1.0',
      url='http://github.com/joeheyming/redef',
      maintainer_email='joeheyming@gmail.com',
      maintainer='Joe Heyming',
      description='Test utility for redefining functions',
      download_url='https://github.com/joeheyming/redef/zipball/master',
      license='GNU GPLv3, Python License',
      long_description="""

redef was inspired by `Test::Resub
<http://search.cpan.org/~airwave/Test-Resub-1.02/lib/Test/Resub.pm>`_.

Sometimes you want to mock a bunch of test functions or objects and have the framework cleanup after you are done.  That is the philosophy of Test::Resub and redef.

All you have to do is - ::
    from redef import redef
    import unittest

    from mymodule import Myobj

    class MyTest(unittest):
        def test_something(self):
            rd_foo = redef(Myobj, 'foo', lambda s: 'bar')
            assertEquals(Myobj().foo, 'bar')

This example is trivial, but you can do some powerful things when you know the expected inputs of a function that is not behaving in your tests.  All you have to do is redef the bad function and make it return what you want to simulate.
""",
      platforms = 'any',
      py_modules = ['redef'],
      # package_dir =  {'': 'lib'},
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'
    ]

      )
