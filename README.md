# fprettify

[![CI](https://github.com/pseewald/fprettify/actions/workflows/test.yml/badge.svg)](https://github.com/pseewald/fprettify/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pseewald/fprettify/badge.svg?branch=master)](https://coveralls.io/github/pseewald/fprettify?branch=master)
![PyPI - License](https://img.shields.io/pypi/l/fprettify)
![PyPI](https://img.shields.io/pypi/v/fprettify)
[![Code Climate](https://codeclimate.com/github/pseewald/fprettify/badges/gpa.svg)](https://codeclimate.com/github/pseewald/fprettify)

fprettify is an auto-formatter for modern Fortran code that imposes strict whitespace formatting, written in Python.

**NOTE:** I'm looking for help to maintain this repository, see [#127](https://github.com/pseewald/fprettify/issues/127).

## Features

- Auto-indentation.
- Line continuations are aligned with the previous opening delimiter `(`, `[` or `(/` or with an assignment operator `=` or `=>`. If none of the above is present, a default hanging indent is applied.
- Consistent amount of whitespace around operators and delimiters.
- Removal of extraneous whitespace and consecutive blank lines.
- Change letter case (upper case / lower case conventions) of intrinsics
- Tested for editor integration.
- By default, fprettify causes whitespace changes only and thus preserves revision history.
- fprettify can handle cpp and [fypp](https://github.com/aradi/fypp) preprocessor directives.

## Limitations

- Works only for modern Fortran (Fortran 90 upwards).
- Feature missing? Please create an issue.

## Requirements

- Python 3 (Python 2.7 no longer supported)
- [ConfigArgParse](https://pypi.org/project/ConfigArgParse): optional, enables use of config file

## Examples

Compare `examples/*before.f90` (original Fortran files) with `examples/*after.f90` (reformatted Fortran files) to see what fprettify does. A quick demonstration:

```Fortran
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

```Fortran
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

```sh
pip install --upgrade fprettify
```

Installation from source requires Python Setuptools:

```sh
pip install .
```

For local installation, use `--user` option.

If you use the [Conda](https://docs.conda.io/) package manager, fprettify is available from the [conda-forge](https://conda-forge.org/) channel:

```sh
conda install -c conda-forge fprettify
```

## Command line tool

Autoformat file1, file2, ... inplace by

```sh
fprettify file1, file2, ...
```

The default indent is 3. If you prefer something else, use `--indent n` argument.

In order to apply fprettify recursively to an entire Fortran project instead of a single file, use the `-r` option.

For more options, read

```sh
fprettify -h
```

## Editor integration

For editor integration, use

```sh
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

When contributing new features by opening a pull request, testing is essential
to verify that the new features behave as intended, and that there are no
unwanted side effects. It is expected that before merging a pull request:
1. one or more unit tests are added which test formatting of small Fortran code
   snippets, covering all relevant aspects of the added features.
2. if the changes lead to failures of existing tests, these test failures
   should be carefully examinated. Only if the test failures are due to
   intended changes of `fprettify` defaults, or because of bug fixes, the
   expected test results can be updated.

### How to add a unit test

Can the new feature be reasonably covered by small code snippets (< 10 lines)?
- Yes: add a test by starting from the following skeleton, and by adding the code to the file `fprettify/tests/unittests.py`:

```python
    def test_something(self):
        """short description"""

        in = "Some Fortran code"
        out = "Same Fortran code after fprettify formatting"

        # seleced fprettify command line arguments, as documented in "fprettify.py -h":
        opt = ["arg 1", "value for arg 1", "arg2", ...] 

        # helper function checking that fprettify output is equal to "out":
        self.assert_fprettify_result(opt, in, out)
```

  Then run `./run_tests.py -s unittests` and check in the output that the newly added unit test passes.


- No: add a test by adding an example Fortran source file: Add the Fortran file
  to `examples/in`, and the reformatted `fprettify` output to `examples/out`.
  If the test requires non-default `fprettify` options, specify these options
  as an annotation `! fprettify:` followed by the command-line arguments at the
  beginning of the Fortran file. You need to manually remove
  `fortran_tests/test_code/examples` to make sure that the test configuration
  will be updated with the changes from `examples`.

  Then run `./run_tests.py -s builtin`, and check that the output mentions the
  newly added example with `checksum new ok`. Check that a new line containing
  the checksum for this example has been added to the file
  `fortran_tests/test_results/expected_results`, and commit this change along
  with your example. Rerun `./run_tests.py -s builtin` and check that the
  output mentions the newly added example with `checksum ok`.

### How to locally run all unit and integration tests:

Run

1. unit tests: `./run_tests.py -s unittests`
2. builtin examples integration tests: `./run_tests.py -s builtin`
3. `regular` integration test suite: `./run_tests.py -s regular`
4. `cron` integration test suite (optional, takes a long time to execute): `./run_tests.py -s cron`

### How to debug test failures

Unit test failures should be rather easy to understand because the test output shows the diff of the actual vs. expected result. For integration tests, we don't store the Fortran code (as it's usually external to this repository), and the result is verified by comparing the SHA256 checksums of the actual vs. expected result. The test output shows the diff of the actual result vs. the previously tested version of the code. Thus, in order to obtain the diff of the actual vs. expected result, the following steps need to be executed:

1. Run `./run_tests.py -s` followed by the name of the failed test suite. Check
   the test output for lines mentioning test failures such as: 
   `Test top-level-dir/subdir/file.f (fprettify.tests.fortrantests.FprettifyIntegrationTestCase) ... checksum FAIL`.
2. Check out a version of `fprettify` for which the test passes.
3. Run the integration test(s) via `./run_tests.py -n top-level-dir` (replacing
   `top-level-dir` with the actual directory mentioned in the test output).
4. Now the `diff` shown in the test output refers to the expected result.

`fprettify` comes with **unit tests**, typically testing expected formatting of smaller code snippets. These tests are entirely self-contained, insofar as the Fortran code, the fprettify options and the expected formatting results are all set within the respective test method. `fprettify` also allows to configure **integration tests** to test expected formatting of external Fortran code. **Unit tests** are relevant when adding new features to `fprettify`, and when these features can easily be tested by small code snippets. **Integration tests** are relevant when an entire Fortran module or program is needed to test a specific feature, or when an external repository relying on `fprettify` should be checked regularly for invariance under `fprettify` formatting.


Run single unit test:

```python
python3 -m unittest -v fprettify.tests.unittests.FprettifyUnitTestCase.test_whitespace
```

The testing mechanism allows you to easily test fprettify with any Fortran project of your choice. Simply clone or copy your entire project into `fortran_tests/before` and run `python setup.py test`. The directory `fortran_tests/after` contains the test output (reformatted Fortran files). If testing fails, please submit an issue!
