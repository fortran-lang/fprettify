from fprettify.aligner import F90Aligner
from fprettify.parser import *
from fprettify.utils import log_message


class F90Indenter:
    """
    Parses encapsulation of subunits / scopes line by line
    and updates the indentation.
    """

    def __init__(self, scope_parser, first_indent, rel_indent, filename):
        # scopes / subunits:
        self._scope_storage = []
        # indents for all fortran lines:
        self._indent_storage = []
        # indents of actual lines of current fortran line
        self._line_indents = []

        self._parser = scope_parser

        self._filename = filename
        self._aligner = F90Aligner(filename)

        # no lines have been processed yet:
        self._initial = True

        # implicit scopes: we define implicit scopes, as many as match
        # first_indent and rel_indent. This allows for, e.g., a properly
        # indented "END FUNCTION" without matching "FUNCTION" statement:
        if rel_indent > 0:
            for n_impl in range(
                first_indent % rel_indent, first_indent + 1, rel_indent
            ):
                self._indent_storage += [n_impl]

        if not self._indent_storage:
            self._indent_storage = [0]

    def process_lines_of_fline(
        self,
        f_line,
        lines,
        rel_ind,
        rel_ind_con,
        line_nr,
        indent_fypp=True,
        manual_lines_indent=None,
    ):
        """
        Process all lines that belong to a Fortran line `f_line`.

        Impose a relative indent of `rel_ind` for current Fortran line,
        and `rel_ind_con` for line continuation.
        By default line continuations are auto-aligned by F90Aligner
        :param f_line: fortran line
        :param lines: actual lines belonging to f_line
        :param rel_ind: relative scope indent size for this line
        :rel_ind_con: relative continuation indent size for this line
        :line_nr: line number
        :indent_fypp: whether or not to include fypp preprocessor lines
        :manual_lines_indent: don't use F90Aligner but manually impose
                              indents for continuations
        """

        if self._initial and (PROG_RE.match(f_line) or MOD_RE.match(f_line)):
            self._indent_storage[-1] = 0

        self._line_indents = [0] * len(lines)
        br_indent_list = [0] * len(lines)

        # local variables to avoid self hassle:
        line_indents = self._line_indents

        scopes = self._scope_storage
        indents = self._indent_storage
        filename = self._filename

        # check statements that start new scope
        is_new = False
        valid_new = False

        f_filter = CharFilter(f_line, filter_fypp=not indent_fypp)
        f_line_filtered = f_filter.filter_all()

        for new_n, newre in enumerate(self._parser["new"]):
            if (
                newre
                and newre.search(f_line_filtered)
                and not self._parser["end"][new_n].search(f_line_filtered)
            ):
                what_new = new_n
                is_new = True
                valid_new = True
                scopes.append(what_new)
                log_message(
                    "{}: {}".format(what_new, f_line), "debug", filename, line_nr
                )

        # check statements that continue scope
        is_con = False
        valid_con = False
        for con_n, conre in enumerate(self._parser["continue"]):
            if conre and conre.search(f_line_filtered):
                what_con = con_n
                is_con = True
                log_message(
                    "{}: {}".format(what_con, f_line), "debug", filename, line_nr
                )
                if len(scopes) > 0:
                    what = scopes[-1]
                    if what == what_con or indent_fypp:
                        valid_con = True

        # check statements that end scope
        is_end = False
        valid_end = False
        for end_n, endre in enumerate(self._parser["end"]):
            if endre and endre.search(f_line_filtered):
                what_end = end_n
                is_end = True
                log_message(
                    "{}: {}".format(what_end, f_line), "debug", filename, line_nr
                )
                if len(scopes) > 0:
                    what = scopes.pop()
                    if (
                        what == what_end
                        or not self._parser["end"][what_end].spec
                        or indent_fypp
                    ):
                        valid_end = True
                        log_message(
                            "{}: {}".format(what_end, f_line),
                            "debug",
                            filename,
                            line_nr,
                        )
                else:
                    valid_end = True

        # fypp preprocessor scopes may be within continuation lines
        if indent_fypp and len(lines) > 1 and not FYPP_LINE_RE.search(f_line_filtered):

            for new_n, newre in enumerate(PREPRO_NEW_SCOPE):
                for l in lines:
                    if newre and newre.search(l):
                        is_new = True
                        valid_new = True
                        scopes.append(new_n)

            for end_n, endre in enumerate(PREPRO_END_SCOPE):
                for l in lines:
                    if endre and endre.search(l):
                        is_end = True
                        valid_end = True
                        if len(scopes) > 0:
                            what = scopes.pop()

        # deal with line breaks
        if not manual_lines_indent:
            self._aligner.process_lines_of_fline(f_line, lines, rel_ind_con, line_nr)
            br_indent_list = self._aligner.get_lines_indent()
        else:
            br_indent_list = manual_lines_indent

        for pos in range(0, len(lines) - 1):
            line_indents[pos + 1] = br_indent_list[pos + 1]

        if is_new and not is_end:
            if not valid_new:
                log_message(
                    "invalid scope opening statement", "info", filename, line_nr
                )

            line_indents = [ind + indents[-1] for ind in line_indents]

            indents.append(rel_ind + indents[-1])

        elif (not is_new) and (is_con or is_end):
            valid = valid_con if is_con else valid_end

            if not valid:
                line_indents = [ind + indents[-1] for ind in line_indents]
                log_message(
                    "invalid scope closing statement", "info", filename, line_nr
                )
            else:
                if len(indents) > 1 or self._initial:
                    line_indents = [
                        ind + indents[-2 + self._initial] for ind in line_indents
                    ]

            if is_end and valid:
                if len(indents) > 1:
                    indents.pop()
                else:
                    indents[-1] = 0

        else:
            line_indents = [ind + indents[-1] for ind in line_indents]

        # we have processed first line:
        self._initial = False

        # reassigning self.* to the updated variables
        self._line_indents = line_indents
        self._scope_storage = scopes
        self._indent_storage = indents

    def get_fline_indent(self):
        """after processing, retrieve the indentation of the full Fortran line."""
        return self._indent_storage[-1]

    def get_lines_indent(self):
        """after processing, retrieve the indents of all line parts."""
        return self._line_indents
