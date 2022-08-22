# fprettify

[![Build Status](https://travis-ci.com/pseewald/fprettify.svg?branch=master)](https://travis-ci.com/pseewald/fprettify) [![Coverage Status](https://coveralls.io/repos/github/pseewald/fprettify/badge.svg?branch=master)](https://coveralls.io/github/pseewald/fprettify?branch=master) [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) [![PyPI version](https://badge.fury.io/py/fprettify.svg)](https://badge.fury.io/py/fprettify)

fprettify is an auto-formatter for modern Fortran code that imposes strict whitespace formatting, written in Python.

**NOTE:** I'm looking for help to maintain this repository, see [#127](https://github.com/pseewald/fprettify/issues/127).


## Features

* Auto-indentation.
* Line continuations are aligned with the previous opening delimiter `(`, `[` or `(/` or with an assignment operator `=` or `=>`. If none of the above is present, a default hanging indent is applied.
* Consistent amount of whitespace around operators and delimiters.
* Removal of extraneous whitespace and consecutive blank lines.
* Change letter case (upper case / lower case conventions) of intrinsics
* Tested for editor integration.
* By default, fprettify causes whitespace changes only and thus preserves revision history.
* fprettify can handle cpp and [fypp](https://github.com/aradi/fypp) preprocessor directives.


## Limitations

* Works only for modern Fortran (Fortran 90 upwards).
* Feature missing? Please create an issue.


## Requirements

* Python 3 (Python 2.7 no longer supported)
* [ConfigArgParse](https://pypi.org/project/ConfigArgParse): optional, enables use of config file


## Examples

Compare `examples/*before.f90` (original Fortran files) with `examples/*after.f90` (reformatted Fortran files) to see what fprettify does. A quick demonstration:

``` Fortran
program demo
integer :: endif,if,elseif
integer,DIMENSION(2) :: function
endif=3;if=2
if(endif==2)then
endif=5
elseif=if+4*(endif+&
2**10)
elseif(endif==3)then
function(if)=endif/elseif
print*,endif
endif
end program
```
⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩ `fprettify` ⇩⇩⇩⇩⇩⇩⇩⇩⇩⇩
``` Fortran
program demo
   integer :: endif, if, elseif
   integer, DIMENSION(2) :: function
   endif = 3; if = 2
   if (endif == 2) then
      endif = 5
      elseif = if + 4*(endif + &
                       2**10)
   elseif (endif == 3) then
      function(if) = endif/elseif
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


## Command line tool

Autoformat file1, file2, ... inplace by
```
fprettify file1, file2, ...
```
The default indent is 3. If you prefer something else, use `--indent n` argument.

In order to apply fprettify recursively to an entire Fortran project instead of a single file, use the `-r` option.

For more options, read
```
fprettify -h
```


## Editor integration

For editor integration, use
```
fprettify --silent
```
For instance, with Vim, use fprettify with `gq` by putting the following commands in your `.vimrc`:
```vim
autocmd Filetype fortran setlocal formatprg=fprettify\ --silent
```


## Deactivation and manual formatting (experimental feature)

fprettify can be deactivated for selected lines: a single line followed by an inline comment starting with `!&` is not auto-formatted and consecutive lines that are enclosed between two comment lines `!&<` and `!&>` are not auto-formatted. This is useful for cases where manual alignment is preferred over auto-formatting. Furthermore, deactivation is necessary when non-standard Fortran syntax (such as advanced usage of preprocessor directives) prevents proper formatting. As an example, consider the following snippet of fprettify formatted code:
```fortran
A = [-1, 10, 0, &
     0, 1000, 0, &
     0, -1, 1]
```
In order to manually align the columns, fprettify needs to be deactivated by
```fortran
A = [-1,   10, 0, & !&
      0, 1000, 0, & !&
      0,   -1, 1]   !&
```
or, equivalently by
```fortran
!&<
A = [-1,   10, 0, &
      0, 1000, 0, &
      0,   -1, 1]
!&>
```


## Contributing / Testing

The testing mechanism allows you to easily test fprettify with any Fortran project of your choice. Simply clone or copy your entire project into `fortran_tests/before` and run `python setup.py test`. The directory `fortran_tests/after` contains the test output (reformatted Fortran files). If testing fails, please submit an issue!


[![Code Climate](https://codeclimate.com/github/pseewald/fprettify/badges/gpa.svg)](https://codeclimate.com/github/pseewald/fprettify)
