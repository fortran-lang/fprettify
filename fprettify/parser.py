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

"""This is a collection of Fortran parsing utilities."""

import re
from collections import deque

from fprettify.constants import FORMATTER_ERROR_MESSAGE
from fprettify.exceptions import FprettifyParseException

# constants
EOL_STR = r"\s*;?\s*$"  # end of fortran line
EOL_SC = r"\s*;\s*$"  # whether line is ended with semicolon
SOL_STR = r"^\s*"  # start of fortran line
LINEBREAK_STR = r"(&)[\s]*(?:!.*)?$"  # for parsing linebreaks
DEL_OPEN_STR = r"(\(\/?|\[)"  # delimiter open
DEL_CLOSE_STR = r"(\/?\)|\])"  # delimiter close
FYPP_LINE_STR = r"^(#!|#:|\$:|@:)"
FYPP_WITHOUT_PREPRO_STR = r"^(#!|\$:|@:)"
CPP_STR = r"^#[^!:{}]"
COMMENT_LINE_STR = r"^!"
FYPP_OPEN_STR = r"(#{|\${|@{)"
FYPP_CLOSE_STR = r"(}#|}\$|}@)"

# regex flags
RE_FLAGS = re.IGNORECASE | re.UNICODE

# FIXME bad ass regex! variable declaration
VAR_DECL_RE = re.compile(
    r"^ *(?P<type>integer(?: *\* *[0-9]+)?|logical|character(?: *\* *[0-9]+)?|real(?: *\* *[0-9]+)?|complex(?: *\* *[0-9]+)?|type) *(?P<parameters>\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))? *(?P<attributes>(?: *, *[a-zA-Z_0-9]+(?: *\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))?)+)? *(?P<dpnt>::)?(?P<vars>[^\n]+)\n?",
    RE_FLAGS,
)

# omp regex
OMP_COND_RE = re.compile(r"^\s*(!\$ )", RE_FLAGS)
OMP_DIR_RE = re.compile(r"^\s*(!\$OMP)", RE_FLAGS)

# supported preprocessors
NOTFORTRAN_LINE_RE = re.compile(
    r"(" + FYPP_LINE_STR + r"|" + CPP_STR + r"|" + COMMENT_LINE_STR + r")", RE_FLAGS
)
NOTFORTRAN_FYPP_LINE_RE = re.compile(
    r"(" + CPP_STR + r"|" + COMMENT_LINE_STR + r")", RE_FLAGS
)
FYPP_LINE_RE = re.compile(FYPP_LINE_STR, RE_FLAGS)
FYPP_WITHOUT_PREPRO_RE = re.compile(FYPP_WITHOUT_PREPRO_STR, RE_FLAGS)
FYPP_OPEN_RE = re.compile(FYPP_OPEN_STR, RE_FLAGS)
FYPP_CLOSE_RE = re.compile(FYPP_CLOSE_STR, RE_FLAGS)
STR_OPEN_RE = re.compile(r"(" + FYPP_OPEN_STR + r"|" + r"'|\"|!)", RE_FLAGS)
CPP_RE = re.compile(CPP_STR, RE_FLAGS)

# regular expressions for parsing delimiters
DEL_OPEN_RE = re.compile(r"^" + DEL_OPEN_STR, RE_FLAGS)
DEL_CLOSE_RE = re.compile(r"^" + DEL_CLOSE_STR, RE_FLAGS)

# regular expressions for parsing operators
# Note: +/- in real literals and sign operator is ignored
PLUSMINUS_RE = re.compile(r"(?<=[\w\)\]])\s*(\+|-)\s*", RE_FLAGS)
# Note: ** or // (or any multiples of * or /) are ignored
#       we also ignore any * or / before a :: because we may be seeing 'real*8'
MULTDIV_RE = re.compile(
    r"(?<=[\w\)\]])\s*((?<!\*)\*(?!\*)|(?<!/)/(?!/))(?=[\s\w\(])(?!.*::)", RE_FLAGS
)
REL_OP_RE = re.compile(
    r"(?<!\()\s*(\.(?:EQ|NE|LT|LE|GT|GE)\.|(?:==|\/=|<(?!=)|<=|(?<!=)>(?!=)|>=))\s*(?!\))",
    RE_FLAGS,
)
LOG_OP_RE = re.compile(r"\s*(\.(?:AND|OR|EQV|NEQV)\.)\s*", RE_FLAGS)
PRINT_RE = re.compile(r"(?:(?<=\bPRINT)|(?<=\bREAD))\s*(\*,?)\s*", RE_FLAGS)

# empty line regex
EMPTY_RE = re.compile(SOL_STR + r"$", RE_FLAGS)

# statement label regex
STATEMENT_LABEL_RE = re.compile(r"^\s*(\d+\s)(?!" + EOL_STR + ")", RE_FLAGS)

# regular expressions for parsing statements that start, continue or end a subunit:
IF_RE = re.compile(SOL_STR + r"(\w+\s*:)?\s*IF\s*\(.*\)\s*THEN" + EOL_STR, RE_FLAGS)
ELSE_RE = re.compile(SOL_STR + r"ELSE(\s*IF\s*\(.*\)\s*THEN)?" + EOL_STR, RE_FLAGS)
ENDIF_RE = re.compile(SOL_STR + r"END\s*IF(\s+\w+)?" + EOL_STR, RE_FLAGS)
DO_RE = re.compile(SOL_STR + r"(\w+\s*:)?\s*DO(" + EOL_STR + r"|\s+\w)", RE_FLAGS)
ENDDO_RE = re.compile(SOL_STR + r"END\s*DO(\s+\w+)?" + EOL_STR, RE_FLAGS)
SELCASE_RE = re.compile(
    SOL_STR + r"SELECT\s*(CASE|RANK|TYPE)\s*\(.*\)" + EOL_STR, RE_FLAGS
)
CASE_RE = re.compile(
    SOL_STR
    + r"((CASE|RANK|TYPE\s+IS|CLASS\s+IS)\s*(\(.*\)|DEFAULT)|CLASS\s+DEFAULT)"
    + EOL_STR,
    RE_FLAGS,
)
ENDSEL_RE = re.compile(SOL_STR + r"END\s*SELECT" + EOL_STR, RE_FLAGS)
ASSOCIATE_RE = re.compile(SOL_STR + r"ASSOCIATE\s*\(.*\)" + EOL_STR, RE_FLAGS)
ENDASSOCIATE_RE = re.compile(SOL_STR + r"END\s*ASSOCIATE" + EOL_STR, RE_FLAGS)
BLK_RE = re.compile(SOL_STR + r"(\w+\s*:)?\s*BLOCK" + EOL_STR, RE_FLAGS)
ENDBLK_RE = re.compile(SOL_STR + r"END\s*BLOCK(\s+\w+)?" + EOL_STR, RE_FLAGS)
SUBR_RE = re.compile(r"^([^\"']* )?SUBROUTINE\s+\w+\s*(\(.*\))?" + EOL_STR, RE_FLAGS)
ENDSUBR_RE = re.compile(SOL_STR + r"END\s*SUBROUTINE(\s+\w+)?" + EOL_STR, RE_FLAGS)
FCT_RE = re.compile(
    r"^([^\"']* )?FUNCTION\s+\w+\s*(\(.*\))?(\s*RESULT\s*\(\w+\))?" + EOL_STR, RE_FLAGS
)
ENDFCT_RE = re.compile(SOL_STR + r"END\s*FUNCTION(\s+\w+)?" + EOL_STR, RE_FLAGS)
MOD_RE = re.compile(SOL_STR + r"MODULE\s+\w+" + EOL_STR, RE_FLAGS)
ENDMOD_RE = re.compile(SOL_STR + r"END\s*MODULE(\s+\w+)?" + EOL_STR, RE_FLAGS)
SMOD_RE = re.compile(SOL_STR + r"SUBMODULE\s*\(\w+\)\s+\w+" + EOL_STR, RE_FLAGS)
ENDSMOD_RE = re.compile(SOL_STR + r"END\s*SUBMODULE(\s+\w+)?" + EOL_STR, RE_FLAGS)
TYPE_RE = re.compile(
    SOL_STR
    + r"TYPE(\s*,\s*(BIND\s*\(\s*C\s*\)|EXTENDS\s*\(.*\)|ABSTRACT|PUBLIC|PRIVATE))*(\s*,\s*)?(\s*::\s*|\s+)\w+"
    + EOL_STR,
    RE_FLAGS,
)
ENDTYPE_RE = re.compile(SOL_STR + r"END\s*TYPE(\s+\w+)?" + EOL_STR, RE_FLAGS)
PROG_RE = re.compile(SOL_STR + r"PROGRAM\s+\w+" + EOL_STR, RE_FLAGS)
ENDPROG_RE = re.compile(SOL_STR + r"END\s*PROGRAM(\s+\w+)?" + EOL_STR, RE_FLAGS)
INTERFACE_RE = re.compile(
    r"^([^\"']* )?INTERFACE(\s+\w+|\s+(OPERATOR|ASSIGNMENT)\s*\(.*\))?" + EOL_STR,
    RE_FLAGS,
)
ENDINTERFACE_RE = re.compile(
    SOL_STR + r"END\s*INTERFACE(\s+\w+|\s+(OPERATOR|ASSIGNMENT)\s*\(.*\))?" + EOL_STR,
    RE_FLAGS,
)
CONTAINS_RE = re.compile(SOL_STR + r"CONTAINS" + EOL_STR, RE_FLAGS)
ENUM_RE = re.compile(
    SOL_STR + r"ENUM(\s*,\s*(BIND\s*\(\s*C\s*\)))?((\s*::\s*|\s+)\w+)?" + EOL_STR,
    RE_FLAGS,
)
ENDENUM_RE = re.compile(SOL_STR + r"END\s*ENUM(\s+\w+)?" + EOL_STR, RE_FLAGS)
ENDANY_RE = re.compile(SOL_STR + r"END" + EOL_STR, RE_FLAGS)

# Regular expressions for where and forall block constructs
FORALL_RE = re.compile(SOL_STR + r"(\w+\s*:)?\s*FORALL\s*\(.*\)" + EOL_STR, RE_FLAGS)
ENDFORALL_RE = re.compile(SOL_STR + r"END\s*FORALL(\s+\w+)?" + EOL_STR, RE_FLAGS)
WHERE_RE = re.compile(SOL_STR + r"(\w+\s*:)?\s*WHERE\s*\(.*\)" + EOL_STR, RE_FLAGS)
ELSEWHERE_RE = re.compile(
    SOL_STR + r"ELSE\s*WHERE(\(.*\))?(\s*\w+)?" + EOL_STR, RE_FLAGS
)
ENDWHERE_RE = re.compile(SOL_STR + r"END\s*WHERE(\s+\w+)?" + EOL_STR, RE_FLAGS)

# Regular expressions for preprocessor directives
FYPP_DEF_RE = re.compile(SOL_STR + r"#:DEF\s+", RE_FLAGS)
FYPP_ENDDEF_RE = re.compile(SOL_STR + r"#:ENDDEF", RE_FLAGS)
FYPP_IF_RE = re.compile(SOL_STR + r"#:IF\s+", RE_FLAGS)
FYPP_ELIF_ELSE_RE = re.compile(SOL_STR + r"#:(ELIF\s+|ELSE)", RE_FLAGS)
FYPP_ENDIF_RE = re.compile(SOL_STR + r"#:ENDIF", RE_FLAGS)
FYPP_FOR_RE = re.compile(SOL_STR + r"#:FOR\s+", RE_FLAGS)
FYPP_ENDFOR_RE = re.compile(SOL_STR + r"#:ENDFOR", RE_FLAGS)
FYPP_BLOCK_RE = re.compile(SOL_STR + r"#:BLOCK\s+", RE_FLAGS)
FYPP_ENDBLOCK_RE = re.compile(SOL_STR + r"#:ENDBLOCK", RE_FLAGS)
FYPP_CALL_RE = re.compile(SOL_STR + r"#:CALL\s+", RE_FLAGS)
FYPP_ENDCALL_RE = re.compile(SOL_STR + r"#:ENDCALL", RE_FLAGS)
FYPP_MUTE_RE = re.compile(SOL_STR + r"#:MUTE", RE_FLAGS)
FYPP_ENDMUTE_RE = re.compile(SOL_STR + r"#:ENDMUTE", RE_FLAGS)
PRIVATE_RE = re.compile(SOL_STR + r"PRIVATE\s*::", RE_FLAGS)
PUBLIC_RE = re.compile(SOL_STR + r"PUBLIC\s*::", RE_FLAGS)
END_RE = re.compile(
    SOL_STR
    + r"(END)\s*(IF|DO|SELECT|ASSOCIATE|BLOCK|SUBROUTINE|FUNCTION|MODULE|SUBMODULE|TYPE|PROGRAM|INTERFACE|ENUM|WHERE|FORALL)",
    RE_FLAGS,
)

# markups to deactivate formatter
NO_ALIGN_RE = re.compile(SOL_STR + r"&\s*[^\s*]+")

# match namelist names
NML_RE = re.compile(r"(/\w+/)", RE_FLAGS)

# find namelists and data statements
NML_STMT_RE = re.compile(SOL_STR + r"NAMELIST.*/.*/", RE_FLAGS)
DATA_STMT_RE = re.compile(SOL_STR + r"DATA\s+\w", RE_FLAGS)

## Regexp for f90 keywords'
F90_KEYWORDS_RE = re.compile(
    r"\b("
    + "|".join(
        (
            "allocatable",
            "allocate",
            "assign",
            "assignment",
            "backspace",
            "block",
            "call",
            "case",
            "character",
            "close",
            "common",
            "complex",
            "contains",
            "continue",
            "cycle",
            "data",
            "deallocate",
            "dimension",
            "do",
            "double",
            "else",
            "elseif",
            "elsewhere",
            "end",
            "enddo",
            "endfile",
            "endif",
            "entry",
            "equivalence",
            "exit",
            "external",
            "forall",
            "format",
            "function",
            "goto",
            "if",
            "implicit",
            "include",
            "inquire",
            "integer",
            "intent",
            "interface",
            "intrinsic",
            "logical",
            "module",
            "namelist",
            "none",
            "nullify",
            "only",
            "open",
            "operator",
            "optional",
            "parameter",
            "pause",
            "pointer",
            "precision",
            "print",
            "private",
            "procedure",
            "program",
            "public",
            "read",
            "real",
            "recursive",
            "result",
            "return",
            "rewind",
            "save",
            "select",
            "sequence",
            "stop",
            "subroutine",
            "target",
            "then",
            "type",
            "use",
            "where",
            "while",
            "write",
            ## F95 keywords.
            "elemental",
            "pure",
            ## F2003
            "abstract",
            "associate",
            "asynchronous",
            "bind",
            "class",
            "deferred",
            "enum",
            "enumerator",
            "extends",
            "extends_type_of",
            "final",
            "generic",
            "import",
            "non_intrinsic",
            "non_overridable",
            "nopass",
            "pass",
            "protected",
            "same_type_as",
            "value",
            "volatile",
            ## F2008.
            "contiguous",
            "submodule",
            "concurrent",
            "codimension",
            "sync all",
            "sync memory",
            "critical",
            "image_index",
        )
    )
    + r")\b",
    RE_FLAGS,
)

## Regexp whose first part matches F90 intrinsic procedures.
## Add a parenthesis to avoid catching non-procedures.
F90_PROCEDURES_RE = re.compile(
    r"\b("
    + "|".join(
        (
            "abs",
            "achar",
            "acos",
            "adjustl",
            "adjustr",
            "aimag",
            "aint",
            "all",
            "allocated",
            "anint",
            "any",
            "asin",
            "associated",
            "atan",
            "atan2",
            "bit_size",
            "btest",
            "ceiling",
            "char",
            "cmplx",
            "conjg",
            "cos",
            "cosh",
            "count",
            "cshift",
            "date_and_time",
            "dble",
            "digits",
            "dim",
            "dot_product",
            "dprod",
            "eoshift",
            "epsilon",
            "exp",
            "exponent",
            "floor",
            "fraction",
            "huge",
            "iachar",
            "iand",
            "ibclr",
            "ibits",
            "ibset",
            "ichar",
            "ieor",
            "index",
            "int",
            "ior",
            "ishft",
            "ishftc",
            "kind",
            "lbound",
            "len",
            "len_trim",
            "lge",
            "lgt",
            "lle",
            "llt",
            "log",
            "log10",
            "logical",
            "matmul",
            "max",
            "maxexponent",
            "maxloc",
            "maxval",
            "merge",
            "min",
            "minexponent",
            "minloc",
            "minval",
            "mod",
            "modulo",
            "mvbits",
            "nearest",
            "nint",
            "not",
            "pack",
            "precision",
            "present",
            "product",
            "radix",
            ## Real is taken out here to avoid highlighting declarations.
            "random_number",
            "random_seed",
            "range",  ## "real"
            "repeat",
            "reshape",
            "rrspacing",
            "scale",
            "scan",
            "selected_int_kind",
            "selected_real_kind",
            "set_exponent",
            "shape",
            "sign",
            "sin",
            "sinh",
            "size",
            "spacing",
            "spread",
            "sqrt",
            "sum",
            "system_clock",
            "tan",
            "tanh",
            "tiny",
            "transfer",
            "transpose",
            "trim",
            "ubound",
            "unpack",
            "verify",
            ## F95 intrinsic functions.
            "null",
            "cpu_time",
            ## F2003.
            "move_alloc",
            "command_argument_count",
            "get_command",
            "get_command_argument",
            "get_environment_variable",
            "selected_char_kind",
            "wait",
            "flush",
            "new_line",
            "extends",
            "extends_type_of",
            "same_type_as",
            "bind",
            ## F2003 ieee_arithmetic intrinsic module.
            "ieee_support_underflow_control",
            "ieee_get_underflow_mode",
            "ieee_set_underflow_mode",
            ## F2003 iso_c_binding intrinsic module.
            "c_loc",
            "c_funloc",
            "c_associated",
            "c_f_pointer",
            "c_f_procpointer",
            ## F2008.
            "bge",
            "bgt",
            "ble",
            "blt",
            "dshiftl",
            "dshiftr",
            "leadz",
            "popcnt",
            "poppar",
            "trailz",
            "maskl",
            "maskr",
            "shifta",
            "shiftl",
            "shiftr",
            "merge_bits",
            "iall",
            "iany",
            "iparity",
            "storage_size",
            "bessel_j0",
            "bessel_j1",
            "bessel_jn",
            "bessel_y0",
            "bessel_y1",
            "bessel_yn",
            "erf",
            "erfc",
            "erfc_scaled",
            "gamma",
            "hypot",
            "log_gamma",
            "norm2",
            "parity",
            "findloc",
            "is_contiguous",
            "sync images",
            "lock",
            "unlock",
            "image_index",
            "lcobound",
            "ucobound",
            "num_images",
            "this_image",
            ## F2008 iso_fortran_env module.
            "compiler_options",
            "compiler_version",
            ## F2008 iso_c_binding module.
            "c_sizeof",
        )
    )
    + r")\b",
    RE_FLAGS,
)

F90_MODULES_RE = re.compile(
    r"\b("
    + "|".join(
        (
            ## F2003/F2008 module names
            "iso_fortran_env",
            "iso_c_binding",
            "ieee_exceptions",
            "ieee_arithmetic",
            "ieee_features",
        )
    )
    + r")\b",
    RE_FLAGS,
)

## Regexp matching intrinsic operators
F90_OPERATORS_RE = re.compile(
    r"("
    + "|".join(
        [
            r"\." + a + r"\."
            for a in (
                "and",
                "eq",
                "eqv",
                "false",
                "ge",
                "gt",
                "le",
                "lt",
                "ne",
                "neqv",
                "not",
                "or",
                "true",
            )
        ]
    )
    + r")",
    RE_FLAGS,
)

## Regexp for Fortran intrinsic constants
F90_CONSTANTS_RE = re.compile(
    r"\b("
    + "|".join(
        (
            ## F2003 iso_fortran_env constants.
            "input_unit",
            "output_unit",
            "error_unit",
            "iostat_end",
            "iostat_eor",
            "numeric_storage_size",
            "character_storage_size",
            "file_storage_size",
            ## F2003 iso_c_binding constants.
            "c_int",
            "c_short",
            "c_long",
            "c_long_long",
            "c_signed_char",
            "c_size_t",
            "c_int8_t",
            "c_int16_t",
            "c_int32_t",
            "c_int64_t",
            "c_int_least8_t",
            "c_int_least16_t",
            "c_int_least32_t",
            "c_int_least64_t",
            "c_int_fast8_t",
            "c_int_fast16_t",
            "c_int_fast32_t",
            "c_int_fast64_t",
            "c_intmax_t",
            "c_intptr_t",
            "c_float",
            "c_double",
            "c_long_double",
            "c_float_complex",
            "c_double_complex",
            "c_long_double_complex",
            "c_bool",
            "c_char",
            "c_null_char",
            "c_alert",
            "c_backspace",
            "c_form_feed",
            "c_new_line",
            "c_carriage_return",
            "c_horizontal_tab",
            "c_vertical_tab",
            "c_ptr",
            "c_funptr",
            "c_null_ptr",
            "c_null_funptr",
            ## F2008 iso_fortran_env constants.
            "character_kinds",
            "int8",
            "int16",
            "int32",
            "int64",
            "integer_kinds",
            "iostat_inquire_internal_unit",
            "logical_kinds",
            "real_kinds",
            "real32",
            "real64",
            "real128",
            "lock_type",
            "atomic_int_kind",
            "atomic_logical_kind",
        )
    )
    + r")\b",
    RE_FLAGS,
)

F90_INT_RE = r"[-+]?[0-9]+"
F90_FLOAT_RE = r"[-+]?([0-9]+\.[0-9]*|\.[0-9]+)"
F90_NUMBER_RE = "(" + F90_INT_RE + "|" + F90_FLOAT_RE + ")"
F90_FLOAT_EXP_RE = F90_NUMBER_RE + r"[eEdD]" + F90_NUMBER_RE
F90_NUMBER_ALL_RE = "(" + F90_NUMBER_RE + "|" + F90_FLOAT_EXP_RE + ")"
F90_NUMBER_ALL_REC = re.compile(F90_NUMBER_ALL_RE, RE_FLAGS)

## F90_CONSTANTS_TYPES_RE = re.compile(r"\b" + F90_NUMBER_ALL_RE + "_(" + "|".join([a + r"\b" for a in (
F90_CONSTANTS_TYPES_RE = re.compile(
    r"("
    + F90_NUMBER_ALL_RE
    + ")*_("
    + "|".join(
        (
            ## F2003 iso_fortran_env constants.
            ## F2003 iso_c_binding constants.
            "c_int",
            "c_short",
            "c_long",
            "c_long_long",
            "c_signed_char",
            "c_size_t",
            "c_int8_t",
            "c_int16_t",
            "c_int32_t",
            "c_int64_t",
            "c_int_least8_t",
            "c_int_least16_t",
            "c_int_least32_t",
            "c_int_least64_t",
            "c_int_fast8_t",
            "c_int_fast16_t",
            "c_int_fast32_t",
            "c_int_fast64_t",
            "c_intmax_t",
            "c_intptr_t",
            "c_float",
            "c_double",
            "c_long_double",
            "c_float_complex",
            "c_double_complex",
            "c_long_double_complex",
            "c_bool",
            "c_char",
            ## F2008 iso_fortran_env constants.
            "character_kinds",
            "int8",
            "int16",
            "int32",
            "int64",
            "integer_kinds",
            "logical_kinds",
            "real_kinds",
            "real32",
            "real64",
            "real128",
            "lock_type",
            "atomic_int_kind",
            "atomic_logical_kind",
        )
    )
    + r")\b",
    RE_FLAGS,
)


def get_curr_delim(line, pos):
    """get delimiter token in line starting at pos, if it exists"""
    what_del_open = DEL_OPEN_RE.search(line[pos : pos + 2])
    what_del_close = DEL_CLOSE_RE.search(line[pos : pos + 2])
    return [what_del_open, what_del_close]


class fline_parser:
    def __init__(self):
        pass

    def search(self, line):
        pass


class parser_re(fline_parser):
    def __init__(self, regex, spec=True):
        self._re = regex
        self.spec = spec

    def search(self, line):
        return self._re.search(line)

    def split(self, line):
        return self._re.split(line)


class plusminus_parser(parser_re):
    """parser for +/- in addition"""

    def __init__(self, regex):
        self._re = regex
        self._re_excl = re.compile(r"\b(\d+\.?\d*|\d*\.?\d+)[de]" + EOL_STR, RE_FLAGS)

    def split(self, line):
        partsplit = self._re.split(line)
        partsplit_out = []

        # exclude splits due to '+/-' in real literals
        for n, part in enumerate(partsplit):
            if re.search(r"^(\+|-)$", part):
                if self._re_excl.search(partsplit[n - 1]):
                    if n == 1:
                        partsplit_out = [partsplit[n - 1]]
                    if n + 1 >= len(partsplit) or not partsplit_out:
                        raise FprettifyParseException(
                            "non-standard expression involving + or -", "", 0
                        )
                    partsplit_out[-1] += part + partsplit[n + 1]
                else:
                    if n == 1:
                        partsplit_out = [partsplit[n - 1]]
                    if n + 1 >= len(partsplit):
                        raise FprettifyParseException(
                            "non-standard expression involving + or -", "", 0
                        )
                    partsplit_out += [part, partsplit[n + 1]]

        if not partsplit_out:
            partsplit_out = partsplit

        return partsplit_out


class where_parser(parser_re):
    """parser for where / forall construct"""

    def search(self, line):
        match = self._re.search(line)

        if match:
            level = 0
            for pos, char in CharFilter(line):
                [what_del_open, what_del_close] = get_curr_delim(line, pos)

                if what_del_open:
                    if what_del_open.group() == r"(":
                        level += 1

                if what_del_close and what_del_close.group() == r")":
                    if level == 1:
                        if EMPTY_RE.search(line[pos + 1 :]):
                            return True
                        else:
                            return False
                    else:
                        level += -1

        return False


def build_scope_parser(fypp=True, mod=True):
    parser = {}
    parser["new"] = [
        parser_re(IF_RE),
        parser_re(DO_RE),
        parser_re(SELCASE_RE),
        parser_re(SUBR_RE),
        parser_re(FCT_RE),
        parser_re(INTERFACE_RE),
        parser_re(TYPE_RE),
        parser_re(ENUM_RE),
        parser_re(ASSOCIATE_RE),
        None,
        parser_re(BLK_RE),
        where_parser(WHERE_RE),
        where_parser(FORALL_RE),
    ]

    parser["continue"] = [
        parser_re(ELSE_RE),
        None,
        parser_re(CASE_RE),
        parser_re(CONTAINS_RE),
        parser_re(CONTAINS_RE),
        None,
        parser_re(CONTAINS_RE),
        None,
        None,
        None,
        None,
        parser_re(ELSEWHERE_RE),
        None,
    ]

    parser["end"] = [
        parser_re(ENDIF_RE),
        parser_re(ENDDO_RE),
        parser_re(ENDSEL_RE),
        parser_re(ENDSUBR_RE),
        parser_re(ENDFCT_RE),
        parser_re(ENDINTERFACE_RE),
        parser_re(ENDTYPE_RE),
        parser_re(ENDENUM_RE),
        parser_re(ENDASSOCIATE_RE),
        parser_re(ENDANY_RE, spec=False),
        parser_re(ENDBLK_RE),
        parser_re(ENDWHERE_RE),
        parser_re(ENDFORALL_RE),
    ]

    if mod:
        parser["new"].extend(
            [parser_re(MOD_RE), parser_re(SMOD_RE), parser_re(PROG_RE)]
        )
        parser["continue"].extend(
            [parser_re(CONTAINS_RE), parser_re(CONTAINS_RE), parser_re(CONTAINS_RE)]
        )
        parser["end"].extend(
            [parser_re(ENDMOD_RE), parser_re(ENDSMOD_RE), parser_re(ENDPROG_RE)]
        )

    if fypp:
        parser["new"].extend(PREPRO_NEW_SCOPE)
        parser["continue"].extend(PREPRO_CONTINUE_SCOPE)
        parser["end"].extend(PREPRO_END_SCOPE)

    return parser


PREPRO_NEW_SCOPE = [
    parser_re(FYPP_DEF_RE),
    parser_re(FYPP_IF_RE),
    parser_re(FYPP_FOR_RE),
    parser_re(FYPP_BLOCK_RE),
    parser_re(FYPP_CALL_RE),
    parser_re(FYPP_MUTE_RE),
]
PREPRO_CONTINUE_SCOPE = [None, parser_re(FYPP_ELIF_ELSE_RE), None, None, None, None]
PREPRO_END_SCOPE = [
    parser_re(FYPP_ENDDEF_RE),
    parser_re(FYPP_ENDIF_RE),
    parser_re(FYPP_ENDFOR_RE),
    parser_re(FYPP_ENDBLOCK_RE),
    parser_re(FYPP_ENDCALL_RE),
    parser_re(FYPP_ENDMUTE_RE),
]

# two-sided operators
LR_OPS_RE = [REL_OP_RE, LOG_OP_RE, plusminus_parser(PLUSMINUS_RE), MULTDIV_RE, PRINT_RE]

USE_RE = re.compile(
    SOL_STR + "USE(\s+|(,.+?)?::\s*)\w+?((,.+?=>.+?)+|,\s*only\s*:.+?)?$" + EOL_STR,
    RE_FLAGS,
)


class CharFilter:
    """
    An iterator to wrap the iterator returned by `enumerate(string)`
    and ignore comments and characters inside strings
    """

    def __init__(
        self, string, filter_comments=True, filter_strings=True, filter_fypp=True
    ):
        self._content = string
        self._it = enumerate(self._content)
        self._instring = ""
        self._infypp = False
        self._incomment = ""
        self._instring = ""
        self._filter_comments = filter_comments
        self._filter_strings = filter_strings
        if filter_fypp:
            self._notfortran_re = NOTFORTRAN_LINE_RE
        else:
            self._notfortran_re = NOTFORTRAN_FYPP_LINE_RE

    def update(
        self, string, filter_comments=True, filter_strings=True, filter_fypp=True
    ):
        self._content = string
        self._it = enumerate(self._content)
        self._filter_comments = filter_comments
        self._filter_strings = filter_strings
        if filter_fypp:
            self._notfortran_re = NOTFORTRAN_LINE_RE
        else:
            self._notfortran_re = NOTFORTRAN_FYPP_LINE_RE

    def __iter__(self):
        return self

    def __next__(self):

        pos, char = next(self._it)

        char2 = self._content[pos : pos + 2]

        if not self._instring:
            if not self._incomment:
                if FYPP_OPEN_RE.search(char2):
                    self._instring = char2
                    self._infypp = True
                elif self._notfortran_re.search(char2):
                    self._incomment = char
                elif char in ['"', "'"]:
                    self._instring = char
        else:
            if self._infypp:
                if FYPP_CLOSE_RE.search(char2):
                    self._instring = ""
                    self._infypp = False
                    if self._filter_strings:
                        self.__next__()
                        return self.__next__()

            elif char in ['"', "'"]:
                if self._instring == char:
                    self._instring = ""
                    if self._filter_strings:
                        return self.__next__()

        if self._filter_comments:
            if self._incomment:
                raise StopIteration

        if self._filter_strings:
            if self._instring:
                return self.__next__()

        return (pos, char)

    def filter_all(self):
        filtered_str = ""
        for _, char in self:
            filtered_str += char
        return filtered_str

    def instring(self):
        return self._instring


class InputStream:
    """Class to read logical Fortran lines from a Fortran file."""

    def __init__(self, infile, filter_fypp=True, orig_filename=None):
        if not orig_filename:
            orig_filename = infile.name
        self.line_buffer = deque([])
        self.infile = infile
        self.line_nr = 0
        self.filename = orig_filename
        self.endpos = deque([])
        self.what_omp = deque([])
        if filter_fypp:
            self.notfortran_re = NOTFORTRAN_LINE_RE
        else:
            self.notfortran_re = NOTFORTRAN_FYPP_LINE_RE

    def next_fortran_line(self):
        """Reads a group of connected lines (connected with &, separated by newline or semicolon)
        returns a touple with the joined line, and a list with the original lines.
        Doesn't support multiline character constants!
        """
        joined_line = ""
        comments = []
        lines = []
        continuation = 0
        fypp_cont = 0
        instring = ""

        string_iter = CharFilter("")
        fypp_cont = 0
        while 1:
            if not self.line_buffer:
                line = self.infile.readline().replace("\t", 8 * " ")
                self.line_nr += 1
                # convert OMP-conditional fortran statements into normal fortran statements
                # but remember to convert them back

                what_omp = OMP_COND_RE.search(line)

                if what_omp:
                    what_omp = what_omp.group(1)
                else:
                    what_omp = ""

                if what_omp:
                    line = line.replace(what_omp, "", 1)
                line_start = 0

                pos = -1

                # multiline string: prepend line continuation with '&'
                if string_iter.instring() and not line.lstrip().startswith("&"):
                    line = "&" + line

                # update instead of CharFilter(line) to account for multiline strings
                string_iter.update(line)
                for pos, char in string_iter:
                    if char == ";" or pos + 1 == len(line):
                        self.endpos.append(pos - line_start)
                        self.line_buffer.append(line[line_start : pos + 1])
                        self.what_omp.append(what_omp)
                        what_omp = ""
                        line_start = pos + 1

                if pos + 1 < len(line):
                    if fypp_cont:
                        self.endpos.append(-1)
                        self.line_buffer.append(line)
                        self.what_omp.append(what_omp)
                    else:
                        for pos_add, char in CharFilter(
                            line[pos + 1 :], filter_comments=False
                        ):
                            char2 = line[pos + 1 + pos_add : pos + 3 + pos_add]
                            if self.notfortran_re.search(char2):
                                self.endpos.append(pos + pos_add - line_start)
                                self.line_buffer.append(line[line_start:])
                                self.what_omp.append(what_omp)
                                break

                if not self.line_buffer:
                    self.endpos.append(len(line))
                    self.line_buffer.append(line)
                    self.what_omp.append("")

            line = self.line_buffer.popleft()
            endpos = self.endpos.popleft()
            what_omp = self.what_omp.popleft()

            if not line:
                break

            lines.append(what_omp + line)

            line_core = line[: endpos + 1]

            if self.notfortran_re.search(line[endpos + 1 : endpos + 3]) or fypp_cont:
                line_comments = line[endpos + 1 :]
            else:
                line_comments = ""

            if line_core:
                newline = line_core[-1] == "\n"
            else:
                newline = False

            line_core = line_core.strip()

            if line_core and not NOTFORTRAN_LINE_RE.search(line_core):
                continuation = 0
            if line_core.endswith("&"):
                continuation = 1

            if line_comments:
                if (
                    FYPP_LINE_RE.search(line[endpos + 1 : endpos + 3]) or fypp_cont
                ) and line_comments.strip()[-1] == "&":
                    fypp_cont = 1
                else:
                    fypp_cont = 0

            line_core = line_core.strip("&")

            comments.append(line_comments.rstrip("\n"))
            if joined_line.strip():
                joined_line = joined_line.rstrip("\n") + line_core + "\n" * newline
            else:
                joined_line = what_omp + line_core + "\n" * newline

            if not (continuation or fypp_cont):
                break

        return (joined_line, comments, lines)


def parse_fprettify_directives(
    lines, comment_lines, in_format_off_block, filename, line_nr
):
    """
    parse formatter directives '!&' and line continuations starting with an
    ampersand.
    """
    auto_align = not any(NO_ALIGN_RE.search(_) for _ in lines)
    auto_format = not (
        in_format_off_block or any(_.lstrip().startswith("!&") for _ in comment_lines)
    )
    if not auto_format:
        auto_align = False
    if (len(lines)) == 1:
        valid_directive = True
        if lines[0].strip().startswith("!&<"):
            if in_format_off_block:
                valid_directive = False
            else:
                in_format_off_block = True
        if lines[0].strip().startswith("!&>"):
            if not in_format_off_block:
                valid_directive = False
            else:
                in_format_off_block = False
        if not valid_directive:
            raise FprettifyParseException(FORMATTER_ERROR_MESSAGE, filename, line_nr)

    return [auto_align, auto_format, in_format_off_block]
