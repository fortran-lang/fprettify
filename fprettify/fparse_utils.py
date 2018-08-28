# -*- coding: utf-8 -*-
###############################################################################
#    This file is part of fprettify.
#    Copyright (C) 2016-2018 Patrick Seewald, CP2K developers group
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

"""This is a collection of Fortran parsing utilities."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import re
from collections import deque

RE_FLAGS = re.IGNORECASE | re.UNICODE

# FIXME bad ass regex!
VAR_DECL_RE = re.compile(
    r"^ *(?P<type>integer(?: *\* *[0-9]+)?|logical|character(?: *\* *[0-9]+)?|real(?: *\* *[0-9]+)?|complex(?: *\* *[0-9]+)?|type) *(?P<parameters>\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))? *(?P<attributes>(?: *, *[a-zA-Z_0-9]+(?: *\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))?)+)? *(?P<dpnt>::)?(?P<vars>[^\n]+)\n?", RE_FLAGS)

# FIXME: unify omp regular expressions
OMP_DIR_RE = re.compile(r"^\s*(!\$omp)", RE_FLAGS)
OMP_RE = re.compile(r"^\s*(!\$)", RE_FLAGS)
OMP_SUBS_RE = re.compile(r"^\s*(!\$(omp)?)", RE_FLAGS)


class FprettifyException(Exception):
    """Base class for all custom exceptions"""

    def __init__(self, msg, filename, line_nr):
        super(FprettifyException, self).__init__(msg)
        self.filename = filename
        self.line_nr = line_nr


class FprettifyParseException(FprettifyException):
    """Exception for unparseable Fortran code (user's fault)."""

    pass


class FprettifyInternalException(FprettifyException):
    """Exception for potential internal errors (fixme's)."""

    pass


class CharFilter(object):
    """
    An iterator to wrap the iterator returned by `enumerate(string)`
    and ignore comments and characters inside strings
    """

    def __init__(self, string, filter_comments=True, filter_strings=True):
        self._content = string
        self._it = enumerate(self._content)
        self._instring = ''
        self._incomment = ''
        self._filter_comments = filter_comments
        self._filter_strings = filter_strings

    def __iter__(self):
        return self

    def next(self):
        """ Python 2 compatibility """
        return self.__next__()

    def __next__(self):

        # make sure that we are not dealing with multiline strings
        # this will go away with multiline strings support
        try:
            pos, char = next(self._it)
        except StopIteration:
            if self._instring:
                raise FprettifyInternalException(
                        "multiline strings not supported", '', 0)
            else:
                raise

        if not self._instring and (char == '!' or char == '#'):
            self._incomment = char

        # detect start/end of a string
        if not self._incomment and char in ['"', "'"]:
            if self._instring == char:
                self._instring = ''
                if self._filter_strings:
                    return self.__next__()
            elif not self._instring:
                self._instring = char

        if self._filter_comments:
            if self._incomment:
                raise StopIteration

        if self._filter_strings:
            if self._instring:
                return self.__next__()

        return (pos, char)


class InputStream(object):
    """Class to read logical Fortran lines from a Fortran file."""

    def __init__(self, infile, orig_filename=None):
        if not orig_filename:
            orig_filename = infile.name
        self.line_buffer = deque([])
        self.infile = infile
        self.line_nr = 0
        self.filename = orig_filename
        self.endpos = deque([])
        self.what_omp = deque([])

    def next_fortran_line(self):
        """Reads a group of connected lines (connected with &, separated by newline or semicolon)
        returns a touple with the joined line, and a list with the original lines.
        Doesn't support multiline character constants!
        """
        joined_line = ""
        comments = []
        lines = []
        continuation = 0
        instring = ''

        while 1:
            if not self.line_buffer:
                line = self.infile.readline().replace("\t", 8 * " ")
                self.line_nr += 1
                # convert OMP-conditional fortran statements into normal fortran statements
                # but remember to convert them back
                what_omp = ''
                if OMP_SUBS_RE.search(line):
                    what_omp = OMP_SUBS_RE.search(line).group(1)
                    line = line.replace(what_omp, '', 1)
                line_start = 0

                pos = -1
                for pos, char in CharFilter(line):
                    if char == ';' or pos + 1 == len(line):
                        self.endpos.append(pos - line_start)
                        self.line_buffer.append(line[line_start:pos + 1])
                        self.what_omp.append(what_omp)
                        what_omp = ''
                        line_start = pos + 1

                if pos + 1 < len(line):
                    for pos_add, char in CharFilter(line[pos+1:], filter_comments=False):
                        if char in ['!', '#']:
                            self.endpos.append(pos + pos_add - line_start)
                            self.line_buffer.append(line[line_start:])
                            self.what_omp.append(what_omp)
                            break

            if self.line_buffer:
                line = self.line_buffer.popleft()
                endpos = self.endpos.popleft()
                what_omp = self.what_omp.popleft()

            if not line:
                break

            lines.append(what_omp + line)

            line_core = line[:endpos + 1]

            try:
                if line[endpos + 1] in ['!', '#']:
                    line_comments = line[endpos + 1:]
                else:
                    line_comments = ''
            except IndexError:
                line_comments = ''

            if line_core:
                newline = (line_core[-1] == '\n')
            else:
                newline = False

            line_core = line_core.strip()

            if line_core:
                continuation = 0
            if line_core.endswith('&'):
                continuation = 1

            line_core = line_core.strip('&')

            comments.append(line_comments.rstrip('\n'))
            if joined_line.strip():
                joined_line = joined_line.rstrip(
                    '\n') + line_core + '\n' * newline
            else:
                joined_line = what_omp + line_core + '\n' * newline

            if not continuation:
                break

        return (joined_line, comments, lines)
