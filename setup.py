#!/usr/bin/env python

from setuptools import setup

setup(name='fprettify',
      version='0.3',
      description='auto-formatter for modern fortran source code',
      author='Patrick Seewald, Ole Schuett, Tiziano Mueller, Mohamed Fawzi',
      license='GPLv3',
      entry_points={'console_scripts': ['fprettify = fprettify:run']},
      packages=['fprettify'],
      test_suite='fprettify.tests',
      )
