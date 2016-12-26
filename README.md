# fprettify
[![Build Status](https://travis-ci.org/pseewald/fprettify.svg?branch=master)](https://travis-ci.org/pseewald/fprettify) [![Coverage Status](https://coveralls.io/repos/github/pseewald/fprettify/badge.svg?branch=master)](https://coveralls.io/github/pseewald/fprettify?branch=master)

fprettify is an auto-formatter for modern Fortran code that imposes strict whitespace formatting.


## Features

* Auto-indentation.
* Line continuations are aligned with the previous opening delimiter `(`, `[` or `(/` or with an assignment operator `=` or `=>`. If none of the above is present, a default hanging indent is applied.
* All operators are surrounded by exactly one whitespace character, except for arithmetic operators.
* Removal of extraneous whitespace and consecutive blank lines.
* Works only for modern Fortran (Fortran 90 upwards).


## Requirements

Python 2.7 or Python 3.x


## Examples

Compare `examples/*before.f90` (original Fortran files) with `examples/*after.f90` (reformatted Fortran files) to see what fprettify does.


## Installation

Requires Python Setuptools.
```
./setup.py install
```

For local installation, use `--user` option.


## Usage

```
fprettify file1, file2, ...
```
The default indent is 3. If you prefer something else, use `--indent=<n>` argument.

For editor integration, use
```
fprettify --no-report-errors
```

For more information, read
```
fprettify --help
```


## Testing

The testing mechanism allows you to easily test fprettify with any Fortran project of your choice. Simply clone or copy your entire project into `fortran_tests/before` and run `python setup.py test`. The directory `fortran_tests/after` contains the test output (reformatted Fortran files). If testing fails, please submit an issue!
