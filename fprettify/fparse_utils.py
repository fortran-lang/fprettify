"""This is a collection of Fortran parsing utilities."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import re
from collections import deque

RE_FLAGS = re.IGNORECASE | re.UNICODE

# FIXME bad ass regex!
VAR_DECL_RE = re.compile(
    r"^ *(?P<type>integer(?: *\* *[0-9]+)?|logical|character(?: *\* *[0-9]+)?|real(?: *\* *[0-9]+)?|complex(?: *\* *[0-9]+)?|type) *(?P<parameters>\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))? *(?P<attributes>(?: *, *[a-zA-Z_0-9]+(?: *\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))?)+)? *(?P<dpnt>::)?(?P<vars>[^\n]+)\n?", RE_FLAGS)

OMP_DIR_RE = re.compile(r"^\s*(!\$omp)", RE_FLAGS)
OMP_RE = re.compile(r"^\s*(!\$)", RE_FLAGS)


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
    An iterator to wrap the iterator returned by `enumerate`
    and ignore comments and characters inside strings
    """

    def __init__(self, it):
        self._it = it
        self._instring = ''

    def __iter__(self):
        return self

    def __next__(self):
        pos, char = next(self._it)
        if not self._instring and char == '!':
            raise StopIteration

        # detect start/end of a string
        if char in ['"', "'"]:
            if self._instring == char:
                self._instring = ''
            elif not self._instring:
                self._instring = char

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
                is_omp_conditional = False
                omp_indent = 0
                if OMP_RE.search(line):
                    omp_indent = len(line) - len(line.lstrip(' '))
                    line = OMP_RE.sub('', line, count=1)
                    is_omp_conditional = True
                line_start = 0
                for pos, char in enumerate(line):
                    if not instring and char == '!':
                        self.endpos.append(pos-1 - line_start)
                        break # ***
                    if char in ['"', "'"]:
                        if instring == char:
                            instring = ''
                        elif not instring:
                            instring = char
                    if not instring:
                        if char == ';' or pos + 1 == len(line):
                            #if re.match(r";\s*$", line[pos:]):
                            #    pos = len(line) - 1
                            self.endpos.append(pos - line_start)
                            self.line_buffer.append(omp_indent * ' ' + '!$' * is_omp_conditional +
                                                    line[line_start:pos + 1])
                            omp_indent = 0
                            is_omp_conditional = False
                            line_start = pos + 1
                            #if pos == len(line) - 1:
                            #    break

                if line_start < len(line):
                    # line + comment
                    # fixme: move to ***
                    self.line_buffer.append('!$' * is_omp_conditional +
                                            line[line_start:])
                    if instring:
                        self.endpos.append(len(line) - line_start)

            if self.line_buffer:
                line = self.line_buffer.popleft()
                endpos = self.endpos.popleft()

            if not line:
                break

            lines.append(line)

            if line.startswith('#'):
                comments.append(line)
                break

            if OMP_RE.search(line) and joined_line.strip():
                # remove omp '!$' for line continuation
                line_core = OMP_RE.sub('', line, count=1).lstrip()
                continue


            line_core = line[:endpos+1]

            try:
                if line[endpos+1] == '!':
                    line_comments=line[endpos+1:]
                else:
                    line_comments=''
            except IndexError:
                line_comments = ''

            # FIXME: line_core should be abstract fortran and it should not
            # matter whether it ends with new line
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
            joined_line = joined_line.rstrip('\n') + line_core + '\n'*newline

            if not continuation:
                break

        #print("joined_line:", joined_line)
        #print("comments:", comments)
        #print("lines:", lines)
        return (joined_line, comments, lines)
