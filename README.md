# fprettify

[![Build Status](https://travis-ci.org/pseewald/fprettify.svg?branch=master)](https://travis-ci.org/pseewald/fprettify) [![Coverage Status](https://coveralls.io/repos/github/pseewald/fprettify/badge.svg?branch=master)](https://coveralls.io/github/pseewald/fprettify?branch=master) [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) [![PyPI version](https://badge.fury.io/py/fprettify.svg)](https://badge.fury.io/py/fprettify)

fprettify is an auto-formatter for modern Fortran code that imposes strict whitespace formatting, written in Python.


## Features

* Auto-indentation.
* Line continuations are aligned with the previous opening delimiter `(`, `[` or `(/` or with an assignment operator `=` or `=>`. If none of the above is present, a default hanging indent is applied.
* Consistent amount of whitespace around operators and delimiters.
* Removal of extraneous whitespace and consecutive blank lines.
* Works only for modern Fortran (Fortran 90 upwards).
* Tested for editor integration.
* By default, fprettify causes changes in the amount of whitespace only and thus preserves revision history.
* Feature missing? Please create an issue.


## Requirements

Python 2.7 or Python 3.x


## Examples

Compare `examples/*before.f90` (original Fortran files) with `examples/*after.f90` (reformatted Fortran files) to see what fprettify does. A quick demonstration:

``` Fortran
program demo
integer :: endif,if,else
endif=3; if=2
if(endif==2)then
endif=5
else=if+4*(endif+&
2**10)
else if(endif==3)then
print*,endif
endif
end program
```
⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩ `fprettify` ⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩
``` Fortran
program demo
   integer :: endif, if, else
   endif = 3; if = 2
   if (endif == 2) then
      endif = 5
      else = if + 4*(endif + &
                     2**10)
   else if (endif == 3) then
      print *, endif
   endif
end program
```


## Installation

The latest release can be installed using pip:
```
pip install --upgrade fprettify
```

Installation from source requires Python Setuptools:
```
./setup.py install
```

For local installation, use `--user` option.


## Usage

Autoformat file1, file2, ... inplace by
```
fprettify file1, file2, ...
```
The default indent is 3. If you prefer something else, use `--indent n` argument. For more options, read
```
fprettify -h
```

For editor integration, use
```
fprettify --silent
```
For instance, with Vim, use fprettify with `gq` by putting the following commands in your `.vimrc`:
```vim
autocmd Filetype fortran setlocal formatprg=fprettify\ --silent
```


## Contributing / Testing

The testing mechanism allows you to easily test fprettify with any Fortran project of your choice. Simply clone or copy your entire project into `fortran_tests/before` and run `python setup.py test`. The directory `fortran_tests/after` contains the test output (reformatted Fortran files). If testing fails, please submit an issue!


[![Code Health](https://landscape.io/github/pseewald/fprettify/master/landscape.svg?style=flat)](https://landscape.io/github/pseewald/fprettify/master) [![Code Climate](https://codeclimate.com/github/pseewald/fprettify/badges/gpa.svg)](https://codeclimate.com/github/pseewald/fprettify) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/d5bb6eeb81ba41478986898d3d2665e4/badge.svg)](https://www.quantifiedcode.com/app/project/d5bb6eeb81ba41478986898d3d2665e4)
