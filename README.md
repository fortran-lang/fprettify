# fprettify

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

Have a look at examples/fortran_after.f90 to see reformatted Fortran code.


## Installation

```
./setup install
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


## Trivia

fprettify is part of the coding conventions of [CP2K](https://www.cp2k.org/) and thus tested with a large code base. Compared with CP2K's internal version (cp2k branch), this version is reduced in functionality. It contains only stable and general features that don't rely on specific coding conventions.
