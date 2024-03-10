from fprettify.exceptions import FprettifyInternalException
from fprettify.parser import *
from fprettify.utils import log_message


class F90Aligner:
    """
    Alignment of continuations of a broken line,
    based on the following heuristics:

    if line break in brackets
        We are parsing the level of nesting
        and align to most inner bracket delimiter.

    else if line is an assignment
        alignment to '=' or '=>'.
        note: assignment operator recognized as any '=' that is not
        part of another operator and that is not enclosed in bracket

    else if line is a declaration
        alignment to '::'

    else
        default indent
    """

    def __init__(self, filename):
        self._filename = filename
        self.__init_line(0)

    def __init_line(self, line_nr):
        """initialization before processing new line"""
        self._line_nr = line_nr
        self._line_indents = [0]
        self._level = 0
        self._br_indent_list = [0]

    def process_lines_of_fline(self, f_line, lines, rel_ind, line_nr):
        """
        process all lines that belong to a Fortran line `f_line`,
        `rel_ind` is the relative indentation size.
        """

        self.__init_line(line_nr)

        is_decl = (
            VAR_DECL_RE.search(f_line)
            or PUBLIC_RE.search(f_line)
            or PRIVATE_RE.match(f_line)
        )
        is_use = USE_RE.search(f_line)
        for pos, line in enumerate(lines):
            self.__align_line_continuations(
                line, is_decl, is_use, rel_ind, self._line_nr + pos
            )
            if pos + 1 < len(lines):
                self._line_indents.append(self._br_indent_list[-1])

        if len(self._br_indent_list) > 2 or self._level:
            log_message(
                "unpaired bracket delimiters", "info", self._filename, self._line_nr
            )

    def get_lines_indent(self):
        """after processing, retrieve the indents of all line parts."""
        return self._line_indents

    def __align_line_continuations(self, line, is_decl, is_use, indent_size, line_nr):
        """align continuation lines."""

        indent_list = self._br_indent_list
        level = self._level
        filename = self._filename

        pos_eq = 0
        pos_ldelim = []
        pos_rdelim = []
        ldelim = []
        rdelim = []

        # find delimiters that are not ended on this line.
        # find proper alignment to most inner delimiter
        # or alignment to assignment operator
        rel_ind = indent_list[-1]  # indentation of prev. line

        end_of_delim = -1

        for pos, char in CharFilter(line):

            what_del_open = None
            what_del_close = None
            if pos > end_of_delim:
                [what_del_open, what_del_close] = get_curr_delim(line, pos)

            if what_del_open:
                what_del_open = what_del_open.group()
                end_of_delim = pos + len(what_del_open) - 1
                level += 1
                indent_list.append(pos + len(what_del_open) + rel_ind)
                pos_ldelim.append(pos)
                ldelim.append(what_del_open)
            if what_del_close:
                what_del_close = what_del_close.group()
                end_of_delim = pos + len(what_del_close) - 1
                if level > 0:
                    level += -1
                    indent_list.pop()
                else:
                    log_message(
                        "unpaired bracket delimiters", "info", filename, line_nr
                    )

                if pos_ldelim:
                    pos_ldelim.pop()
                    what_del_open = ldelim.pop()
                    valid = False
                    if what_del_open == r"(":
                        valid = what_del_close == r")"
                    if what_del_open == r"(/":
                        valid = what_del_close == r"/)"
                    if what_del_open == r"[":
                        valid = what_del_close == r"]"
                    if not valid:
                        log_message(
                            "unpaired bracket delimiters", "info", filename, line_nr
                        )

                else:
                    pos_rdelim.append(pos)
                    rdelim.append(what_del_close)
            if char == "," and not level and pos_eq > 0:
                # a top level comma removes previous alignment position.
                # (see issue #11)
                pos_eq = 0
                indent_list.pop()
            if (
                not level
                and not is_decl
                and char == "="
                and not REL_OP_RE.search(
                    line[max(0, pos - 1) : min(pos + 2, len(line))]
                )
            ):
                # should only have one assignment per line!
                if pos_eq > 0:
                    raise FprettifyInternalException(
                        "found more than one assignment in the same Fortran line",
                        filename,
                        line_nr,
                    )
                is_pointer = line[pos + 1] == ">"
                pos_eq = pos + 1
                # don't align if assignment operator directly before
                # line break
                if not re.search(r"=>?\s*" + LINEBREAK_STR, line, RE_FLAGS):
                    indent_list.append(pos_eq + 1 + is_pointer + indent_list[-1])
            elif (
                is_decl
                and line[pos : pos + 2] == "::"
                and not re.search(r"::\s*" + LINEBREAK_STR, line, RE_FLAGS)
            ):
                indent_list.append(pos + 3 + indent_list[-1])
            elif (
                is_use
                and line[pos] == ":"
                and not re.search(r":\s*" + LINEBREAK_STR, line, RE_FLAGS)
            ):
                indent_list.append(pos + 2 + indent_list[-1])

        # Don't align if delimiter opening directly before line break
        if level and re.search(DEL_OPEN_STR + r"\s*" + LINEBREAK_STR, line, RE_FLAGS):
            if len(indent_list) > 1:
                indent_list[-1] = indent_list[-2]
            else:
                indent_list[-1] = 0

        if not indent_list[-1]:
            indent_list[-1] = indent_size

        self._level = level
