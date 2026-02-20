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

When cleaning up inline comments, `--strip-comments` removes superfluous whitespace in front of comment markers. Combine it with `--comment-spacing N` to specify how many spaces should remain between code and the trailing comment (default: 1).

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
   should be carefully examined. Only if the test failures are due to
   intended changes of `fprettify` defaults, or because of bug fixes, the
   expected test results can be updated.


### How to add a unit test

Can the new feature be reasonably covered by small code snippets (< 10 lines)?
- **Yes**: add a test by starting from the following skeleton, and by adding the code to the file `fprettify/tests/unittests.py`:

```python
    def test_something(self):
        """short description"""

        in = "Some Fortran code"
        out = "Same Fortran code after fprettify formatting"

        # selected fprettify command line arguments, as documented in "fprettify.py -h":
        opt = ["arg 1", "value for arg 1", "arg2", ...] 

        # helper function checking that fprettify output is equal to "out":
        self.assert_fprettify_result(opt, in, out)
```

  Then run `./run_tests.py -s unittests` and check in the output that the newly added unit test passes.


- **No**: add a test by adding an example Fortran source file: Add the Fortran file
  to `examples/in`, and the reformatted `fprettify` output to `examples/out`.
  If the test requires non-default `fprettify` options, specify these options
  as an annotation `! fprettify:` followed by the command-line arguments at the
  beginning of the Fortran file. Then you'll need to manually remove
  `fortran_tests/test_code/examples` to make sure that the test configuration
  will be updated with the changes from `examples`.

Then run `./run_tests.py -s builtin`, and check that the output mentions the
newly added example with `checksum new ok`. Check that a new line containing
the checksum for this example has been added to the file
`fortran_tests/test_results/expected_results`, and commit this change along
with your example. Rerun `./run_tests.py -s builtin` and check that the
output mentions the newly added example with `checksum ok`.


### How to add integration tests

This is a mechanism to add external code bases (such as entire git repositories
containing Fortran code) as test cases. In order to add a new code base as an
integration test suite, add a new section to
[testsuites.config](fortran_tests/testsuites.config), adhering to the following
format:

``INI
[...]        # arbitrary unique section name identifying test code
obtain: ...  # Python command to obtain test code base
path: ...    # relative path pointing to test code location
suite: ...   # which suite this test code should belong to
`` 

For `suite`, you should pick one of the following test suites:
- `regular`: for small code bases (executed for every pull request)
- `cron`: for larger code bases (executed nightly)


### How to locally run all unit and integration tests:

- unit tests: `./run_tests.py -s unittests`
- builtin examples integration tests: `./run_tests.py -s builtin`
- `regular`: integration test suite: `./run_tests.py -s regular`
- `cron`: integration test suite (optional, takes a long time to execute): `./run_tests.py -s cron`
- `custom`: a dedicated test suite for quick testing, shouldn't be committed.


### How to locally run selected unit or integration tests:

- unit tests: run
    `python -m unittest -v fprettify.tests.unittests.FprettifyUnitTestCase.test_xxx`
    (replacing `test_xxx` with the actual name of the test method)
- integration tests: run
    - a specific suite (`unittests`, `builtin`, `regular`, `cron` or `custom`)
      `./run_tests.py -s ...`
    - tests belonging to a config section (see [testsuites.config](fortran_tests/testsuites.config)):
      `./run_tests.py -n ...`
      

### How to deal with test failures

Test failures are always due to fprettify-formatted code being different than
expected. To examine what has changed, proceed as follows:
- Unit tests: failures should be rather easy to understand because the test
  output shows the diff of the actual vs. expected result. 
- Integration tests: we don't store the expected version of Fortran code,
  instead we compare SHA256 checksums of the actual vs. expected result. The
  test output shows the diff of the actual result vs. the *previous* version of
  the code (that is, the version before `fprettify` was applied). Thus, in
  order to obtain the diff of the actual vs. the *expected* result, the
  following steps need to be executed:

  1. Run `./run_tests.py -s` followed by the name of the failed test suite. Check
     the test output for lines mentioning test failures such as: 
     `Test top-level-dir/subdir/file.f (fprettify.tests.fortrantests.FprettifyIntegrationTestCase) ... checksum FAIL`.
  2. Check out the reference version of `fprettify` for which the test passes (normally, `develop` branch).
  3. Run the integration test(s) via `./run_tests.py -n top-level-dir` (replacing
     `top-level-dir` with the actual directory mentioned in the test output).
  4. Check out the version of `fprettify` for which the test failed and run the integration tests again.
  5. Now the `diff` shown in the test output shows the exact changes which caused the test to fail.

If you decide to accept the changes as new test references, proceed as follows:
- Unit tests: update the expected test result within the respective test method (third argument to function `self.assert_fprettify_result`)
- Integration tests: run `./run_tests.py ... -r` and commit the updated `fortran_tests/test_results/expected_results`. Then
  run `./run_tests.py ...` and check that tests are passing now.

