"""Miscellaneous constants"""

FORTRAN_EXTENSIONS = [".f", ".for", ".ftn", ".f90", ".f95", ".f03", ".fpp"]
FORTRAN_EXTENSIONS += [_.upper() for _ in FORTRAN_EXTENSIONS]

FORMATTER_ERROR_MESSAGE = (
    " Wrong usage of formatting-specific directives" " '&', '!&', '!&<' or '!&>'."
)
LINESPLIT_MESSAGE = (
    "auto indentation failed due to chars limit, " "line should be split"
)

# intrinsic statements with parenthesis notation that are not functions
INTR_STMTS_PAR = (
    r"(ALLOCATE|DEALLOCATE|"
    r"OPEN|CLOSE|READ|WRITE|"
    r"FLUSH|ENDFILE|REWIND|BACKSPACE|INQUIRE|"
    r"FORALL|WHERE|ASSOCIATE|NULLIFY)"
)
