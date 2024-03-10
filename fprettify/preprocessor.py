from fprettify.parser import (
    EMPTY_RE,
    FYPP_LINE_RE,
    OMP_COND_RE,
    OMP_DIR_RE,
    STATEMENT_LABEL_RE,
)


def preprocess_omp(f_line, lines):
    """convert omp conditional to normal fortran"""

    is_omp_conditional = bool(OMP_COND_RE.search(f_line))
    if is_omp_conditional:
        f_line = OMP_COND_RE.sub("   ", f_line, count=1)
        lines = [OMP_COND_RE.sub("   ", l, count=1) for l in lines]

    return [f_line, lines, is_omp_conditional]


def preprocess_labels(f_line, lines):
    """remove statement labels"""

    match = STATEMENT_LABEL_RE.search(f_line)
    if match:
        label = match.group(1)
    else:
        label = ""

    if label:
        f_line = STATEMENT_LABEL_RE.sub(len(label) * " ", f_line, count=1)
        lines[0] = STATEMENT_LABEL_RE.sub(len(label) * " ", lines[0], count=1)

    return [f_line, lines, label]


def preprocess_line(f_line, lines, comments, filename, line_nr, indent_fypp):
    """preprocess lines: identification and formatting of special cases"""
    is_blank = False
    prev_indent = False
    do_format = False

    # is_special: special directives that should not be treated as Fortran
    # currently supported: fypp preprocessor directives or comments for FORD documentation
    is_special = [False] * len(lines)

    for pos, line in enumerate(lines):
        line_strip = line.lstrip()
        if indent_fypp:
            is_special[pos] = line_strip.startswith("!!") or (
                FYPP_LINE_RE.search(line_strip) if pos > 0 else False
            )
        else:
            is_special[pos] = FYPP_LINE_RE.search(line_strip) or line_strip.startswith(
                "!!"
            )

    # if first line is special, all lines should be special
    if is_special[0]:
        is_special = [True] * len(lines)

    if EMPTY_RE.search(f_line):  # empty lines including comment lines
        if any(comments):
            if lines[0].startswith(" ") and not OMP_DIR_RE.search(lines[0]):
                # indent comment lines only if they were not indented before.
                prev_indent = True
        else:
            is_blank = True
        lines = [l.strip(" ") if not is_special[n] else l for n, l in enumerate(lines)]
    else:
        do_format = True

    return [lines, do_format, prev_indent, is_blank, is_special]
