#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#    This file is part of fprettify.
#    Copyright (C) 2016-2019 Patrick Seewald, CP2K developers group
#
#    fprettify is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    fprettify is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with fprettify. If not, see <http://www.gnu.org/licenses/>.
###############################################################################

"""
Impose white space conventions and indentation based on scopes / subunits

normalization of white spaces supported for following operators:
- relational operators:
  .EQ. .NE. .LT. .LE. .GT. .GE.
  ==   /=   <    <=    >   >=
- logical operators:
  .AND. .OR. .EQV. .NEQV.
  .NOT.
- bracket delimiters
- commas and semicolons:
- arithmetic operators:
  *  /  **  +  -
- other operators:
  %  - (sign)  = (function argument)
  = (assignment)  => (pointer assignment)

supported criteria for alignment / indentation:
 Fortran lines:
 - if, else, endif
 - do, enddo
 - select case, case, end select
 - select rank, rank, end select
 - subroutine, end subroutine
 - function, end function
 - module, end module
 - program, end program
 - interface, end interface
 - type, end type
 Actual lines (parts of Fortran lines separated by linebreaks):
 - bracket delimiters (.), (/./), and [.]
 - assignments by value = and pointer =>.

LIMITATIONS
- assumes that all subunits are explicitly ended within same file,
  no treatment of #include statements
- can not deal with f77 constructs (files are ignored)

FIXME's
- internal errors should not happen
- wrap regular expression parser. This allows to extend parser by constructs
  that are not regular expressions (and support e.g. forall construct).
- strip whitespaces once and for all and then assume no trailing / leading
  whitespaces
- open files only when needed
"""
import io
import logging
import os
import sys

from fprettify.constants import *
from fprettify.exceptions import *
from fprettify.formatter import reformat
from fprettify.utils import (
    build_ws_dict,
    get_arg_parser,
    get_config_files,
    get_parser_args,
    log_exception,
    set_logger,
)

sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding="UTF-8", line_buffering=True)
sys.stdout = io.TextIOWrapper(
    sys.stdout.detach(), encoding="UTF-8", line_buffering=True
)


def run(argv=sys.argv):  # pragma: no cover
    """Command line interface"""

    parser_args = get_parser_args()
    parser = get_arg_parser(parser_args)
    args = parser.parse_args(argv[1:])

    # support legacy input:
    if "stdin" in args.path and not os.path.isfile("stdin"):
        args.path = ["-" if _ == "stdin" else _ for _ in args.path]

    for directory in args.path:
        if directory == "-":
            if args.recursive:
                sys.stderr.write("--recursive requires a directory.\n")
                sys.exit(1)
        else:
            if not os.path.exists(directory):
                sys.stderr.write("directory " + directory + " does not exist!\n")
                sys.exit(1)
            if (
                not os.path.isfile(directory)
                and directory != "-"
                and not args.recursive
            ):
                sys.stderr.write("file " + directory + " does not exist!\n")
                sys.exit(1)

        if not args.recursive:
            filenames = [directory]
        else:
            ext = args.fortran if args.fortran else FORTRAN_EXTENSIONS
            filenames = []

            from fnmatch import fnmatch

            for dirpath, dirnames, files in os.walk(directory, topdown=True):
                # Prune excluded patterns from list of child directories
                dirnames[:] = [
                    dirname
                    for dirname in dirnames
                    if not any(
                        [
                            fnmatch(dirname, exclude_pattern)
                            or fnmatch(os.path.join(dirpath, dirname), exclude_pattern)
                            for exclude_pattern in args.exclude
                        ]
                    )
                ]

                for ffile in [
                    os.path.join(dirpath, f)
                    for f in files
                    if any(f.endswith(_) for _ in ext)
                    and not any(
                        [
                            fnmatch(f, exclude_pattern)
                            for exclude_pattern in args.exclude
                        ]
                    )
                ]:
                    filenames.append(ffile)

        for filename in filenames:
            # reparse arguments using the file's list of config files
            filearguments = parser_args
            filearguments["default_config_files"] = ["~/.fprettify.rc"] + list(
                get_config_files(
                    os.path.abspath(filename) if filename != "-" else os.getcwd()
                )
            )
            file_argparser = get_arg_parser(filearguments)
            file_args = file_argparser.parse_args(argv[1:])
            ws_dict = build_ws_dict(file_args)
            stdout = file_args.stdout or directory == "-"
            diffonly = file_args.diff
            case_dict = {
                "keywords": file_args.case[0],
                "procedures": file_args.case[1],
                "operators": file_args.case[2],
                "constants": file_args.case[3],
            }

            set_logger(
                logging.DEBUG
                if file_args.debug
                else logging.CRITICAL if args.silent else logging.WARNING
            )

            try:
                # transfer input stream or file to an in-memory buffer
                if filename == "-":
                    ib = io.StringIO()
                    ib.write(sys.stdin.read())
                else:
                    ib = io.open(filename, "r", encoding="utf-8")

                # buffer for reformatted output
                ob = io.StringIO()

                # reformat the input buffer
                reformat(
                    ib,
                    ob,
                    orig_filename=filename,
                    impose_indent=not file_args.disable_indent,
                    indent_size=file_args.indent,
                    strict_indent=file_args.strict_indent,
                    impose_whitespace=not file_args.disable_whitespace,
                    impose_replacements=file_args.enable_replacements,
                    cstyle=file_args.c_relations,
                    case_dict=case_dict,
                    whitespace=file_args.whitespace,
                    whitespace_dict=ws_dict,
                    llength=(
                        1024 if file_args.line_length == 0 else file_args.line_length
                    ),
                    strip_comments=file_args.strip_comments,
                    format_decl=file_args.enable_decl,
                    indent_fypp=not file_args.disable_fypp,
                    indent_mod=not file_args.disable_indent_mod,
                )

                # if in diff mode, just write the diff to stdout
                if diffonly:
                    from fprettify.utils import diff

                    ib.seek(0)
                    ob.seek(0)
                    sys.stdout.write(diff(ib.read(), ob.read(), filename, filename))
                else:
                    # otherwise write reformatted content to the selected output
                    if stdout:
                        sys.stdout.write(ob.getvalue())
                        return

                    # write to output file only if content has changed
                    import hashlib

                    output = ob.getvalue()
                    hash_new = hashlib.md5()
                    hash_new.update(output.encode("utf-8"))
                    hash_old = hashlib.md5()
                    with io.open(filename, "r", encoding="utf-8") as f:
                        hash_old.update(f.read().encode("utf-8"))
                    if hash_new.digest() == hash_old.digest():
                        return
                    with io.open(filename, "w", encoding="utf-8") as f:
                        f.write(output)
            except FprettifyException as e:
                log_exception(e, "Fatal error occured")
                sys.exit(1)
