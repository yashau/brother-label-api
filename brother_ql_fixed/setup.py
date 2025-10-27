# -*- coding: utf-8 -*-
"""
Fixed setup.py for brother_ql - Python 3.9+ compatible
Removed python-future dependency and Python 2 compatibility code
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LDESC = '''
Brother QL - Fixed for Python 3.9+

A Python package to talk to Brother QL label printers.
This is a fixed version that removes the python-future dependency
and works with Python 3.9 through 3.13+.

All functionality from the original package is preserved.
'''

setup(name='brother_ql',
      version = '0.9.5',
      description = 'Python package to talk to Brother QL label printers (Python 3.9+ fixed)',
      long_description = LDESC,
      author = 'Philipp Klaus (original), Python 3.9+ fixes',
      author_email = 'philipp.l.klaus@web.de',
      url = 'https://github.com/pklaus/brother_ql',
      license = 'GPL',
      packages = ['brother_ql',
                  'brother_ql.backends'],
      entry_points = {
          'console_scripts': [
              'brother_ql = brother_ql.cli:cli',
              'brother_ql_analyse = brother_ql.brother_ql_analyse:main',
              'brother_ql_create  = brother_ql.brother_ql_create:main',
              'brother_ql_print   = brother_ql.brother_ql_print:main',
              'brother_ql_debug   = brother_ql.brother_ql_debug:main',
              'brother_ql_info    = brother_ql.brother_ql_info:main',
          ],
      },
      include_package_data = False,
      zip_safe = True,
      platforms = 'any',
      install_requires = [
          "click",
          # "future",  # REMOVED - Not needed for Python 3.9+
          "packbits",
          "pillow>=3.3.0",
          "pyusb",
          'attrs',
          # Removed Python < 3.5 compatibility dependencies
      ],
      extras_require = {
          #'brother_ql_analyse':  ["matplotlib",],
          #'brother_ql_create' :  ["matplotlib",],
      },
      keywords = 'Brother QL-500 QL-550 QL-560 QL-570 QL-700 QL-710W QL-720NW QL-800 QL-810W QL-820NWB QL-1050 QL-1060N',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: System :: Hardware :: Hardware Drivers',
      ]
)
