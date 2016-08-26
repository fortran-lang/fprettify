#!/usr/bin/env python

from setuptools import setup

setup(name='fprettify',
      description='auto-formatter for modern fortran source code',
      author='Patrick Seewald, Ole Schuett, Mohamed Fawzi',
      license = 'GPL',
      entry_points={'console_scripts': ['fprettify = fprettify:main']},
      py_modules=['fprettify','fparse_utils']
     )
