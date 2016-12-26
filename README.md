# fprettify [![Build Status](https://travis-ci.org/pseewald/fprettify.svg?branch=master)](https://travis-ci.org/pseewald/fprettify)

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

Compare examples/\*before.f90 (original Fortran files) with examples/\*after.f90 (reformatted Fortran files) to see what fprettify does.


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


## Contributing

Even though fprettify is tested on a large code base ([CP2K](https://www.cp2k.org/)), there may be cases where it fails. If you find such a case, please let me know by creating an `issue`.
Any contributions are very welcome. Specifically there is more work to be done on experimental features in `cp2k` branch (see below for more details). These features are useful but not yet stable enough to be integrated into `master`.


## cp2k branch

Compared with CP2K's internal version of fprettify (`cp2k` branch), this version (`master` branch) is reduced in functionality. It contains only stable and general features that don't rely on specific coding conventions. The `cp2k` specific features not yet integrated into `master` are:

* Sorting and alignment of variable declarations and `use` statements lists, removal of unused list entries
* All Fortran keywords in upper case

Feel free to try these features by `git checkout cp2k` and read `./fprettify.py --help` for further instructions.
