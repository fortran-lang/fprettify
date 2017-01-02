#!/usr/bin/env python
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(name='fprettify',
      version='0.3.1',
      description='auto-formatter for modern fortran source code',
      long_description=long_description,
      author='Patrick Seewald',
      author_email='patrick.seewald@gmail.com',
      license='GPLv3',
      entry_points={'console_scripts': ['fprettify = fprettify:run']},
      packages=['fprettify'],
      test_suite='fprettify.tests',
      install_requires=['future'],
      keywords='fortran format formatting auto-formatter indent',
      url='https://github.com/pseewald/fprettify',
      download_url= 'https://github.com/pseewald/fprettify/archive/v0.3.1.tar.gz',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Quality Assurance',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Environment :: Console',
          'Operating System :: OS Independent',
      ]
      )
