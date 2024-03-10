"""Custom exception types"""


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
