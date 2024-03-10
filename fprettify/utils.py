import errno
import logging
import os
import sys
from difflib import unified_diff
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import Iterable, List, Optional, Union

import configargparse as argparse

from fprettify.constants import FORTRAN_EXTENSIONS


def build_ws_dict(args):
    # todo: do we need this?
    ws_dict = {}
    ws_dict["comma"] = args.whitespace_comma
    ws_dict["assignments"] = args.whitespace_assignment
    ws_dict["decl"] = args.whitespace_decl
    ws_dict["relational"] = args.whitespace_relational
    ws_dict["logical"] = args.whitespace_logical
    ws_dict["plusminus"] = args.whitespace_plusminus
    ws_dict["multdiv"] = args.whitespace_multdiv
    ws_dict["print"] = args.whitespace_print
    ws_dict["type"] = args.whitespace_type
    ws_dict["intrinsics"] = args.whitespace_intrinsics
    return ws_dict


def get_parser_args():
    return {
        "description": "Auto-format modern Fortran source files. Config files ('.fprettify.rc') in the home (~) directory and any such files located in parent directories of the input file will be used. When the standard input is used, the search is started from the current directory.",
        "formatter_class": argparse.ArgumentDefaultsHelpFormatter,
        "args_for_setting_config_path": ["-c", "--config-file"],
    }


def get_arg_parser(args=None):
    """Create the argument parse for the command line interface."""
    parser = argparse.ArgumentParser(**args)

    parser.add_argument(
        "-i", "--indent", type=int, default=3, help="relative indentation width"
    )
    parser.add_argument(
        "-l",
        "--line-length",
        type=int,
        default=132,
        help="column after which a line should end, viz. -ffree-line-length-n for GCC",
    )
    parser.add_argument(
        "-w",
        "--whitespace",
        type=int,
        choices=range(0, 5),
        default=2,
        help="Presets for the amount of whitespace - "
        "   0: minimal whitespace"
        " | 1: operators (except arithmetic), print/read"
        " | 2: operators, print/read, plus/minus"
        " | 3: operators, print/read, plus/minus, muliply/divide"
        " | 4: operators, print/read, plus/minus, muliply/divide, type component selector",
    )
    parser.add_argument(
        "--whitespace-comma",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for comma/semicolons",
    )
    parser.add_argument(
        "--whitespace-assignment",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for assignments",
    )
    parser.add_argument(
        "--whitespace-decl",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for declarations (requires '--enable-decl')",
    )
    parser.add_argument(
        "--whitespace-relational",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for relational operators",
    )
    parser.add_argument(
        "--whitespace-logical",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for logical operators",
    )
    parser.add_argument(
        "--whitespace-plusminus",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for plus/minus arithmetic",
    )
    parser.add_argument(
        "--whitespace-multdiv",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for multiply/divide arithmetic",
    )
    parser.add_argument(
        "--whitespace-print",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for print/read statements",
    )
    parser.add_argument(
        "--whitespace-type",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for select type components",
    )
    parser.add_argument(
        "--whitespace-intrinsics",
        type=str2bool,
        nargs="?",
        default="None",
        const=True,
        help="boolean, en-/disable whitespace for intrinsics like if/write/close",
    )
    parser.add_argument(
        "--strict-indent",
        action="store_true",
        default=False,
        help="strictly impose indentation even for nested loops",
    )
    parser.add_argument(
        "--enable-decl",
        action="store_true",
        default=False,
        help="enable whitespace formatting of declarations ('::' operator).",
    )
    parser.add_argument(
        "--disable-indent",
        action="store_true",
        default=False,
        help="don't impose indentation",
    )
    parser.add_argument(
        "--disable-whitespace",
        action="store_true",
        default=False,
        help="don't impose whitespace formatting",
    )
    parser.add_argument(
        "--enable-replacements",
        action="store_true",
        default=False,
        help="replace relational operators (e.g. '.lt.' <--> '<')",
    )
    parser.add_argument(
        "--c-relations",
        action="store_true",
        default=False,
        help="C-style relational operators ('<', '<=', ...)",
    )
    parser.add_argument(
        "--case",
        nargs=4,
        default=[0, 0, 0, 0],
        type=int,
        help="Enable letter case formatting of intrinsics by specifying which of "
        "keywords, procedures/modules, operators and constants (in this order) should be lowercased or uppercased - "
        "   0: do nothing"
        " | 1: lowercase"
        " | 2: uppercase",
    )

    parser.add_argument(
        "--strip-comments",
        action="store_true",
        default=False,
        help="strip whitespaces before comments",
    )
    parser.add_argument(
        "--disable-fypp",
        action="store_true",
        default=False,
        help="Disables the indentation of fypp preprocessor blocks.",
    )
    parser.add_argument(
        "--disable-indent-mod",
        action="store_true",
        default=False,
        help="Disables the indentation after module / program.",
    )

    parser.add_argument(
        "-d",
        "--diff",
        action="store_true",
        default=False,
        help="Write file differences to stdout instead of formatting inplace",
    )
    parser.add_argument(
        "-s",
        "--stdout",
        action="store_true",
        default=False,
        help="Write to stdout instead of formatting inplace",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-S",
        "--silent",
        "--no-report-errors",
        action="store_true",
        default=False,
        help="Don't write any errors or warnings to stderr",
    )
    group.add_argument(
        "-D", "--debug", action="store_true", default=False, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "path",
        type=str,
        nargs="*",
        help="Paths to files to be formatted inplace. If no paths are given, stdin (-) is used by default. Path can be a directory if --recursive is used.",
        default=["-"],
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="Recursively auto-format all Fortran files in subdirectories of specified path; recognized filename extensions: {}".format(
            ", ".join(FORTRAN_EXTENSIONS)
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        type=str,
        help="File or directory patterns to be excluded when searching for Fortran files to format",
    )
    parser.add_argument(
        "-f",
        "--fortran",
        type=str,
        action="append",
        default=[],
        help="Overrides default fortran extensions recognized by --recursive. Repeat this option to specify more than one extension.",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.3.7")
    return parser


def get_config_files(path: Union[str, PathLike]) -> List[Path]:
    """Find configuration files in or above the given path."""
    files = []
    path = Path(path).expanduser().absolute()
    if not path.exists():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(path))
    parent = path if path.is_dir() else path.parent
    while True:
        file = parent / ".fprettify.rc"
        if file.is_file():
            files.insert(0, file)
        parent = parent.parent
        if parent == parent:
            break
        parent = parent
    return files


def glob(path, recursive=False, *patterns) -> Iterable[Path]:
    """
    Find pathnames under the given path, optionally recursively,
    matching any of the given patterns.
    """
    if recursive:
        return iter(chain.from_iterable(path.rglob(p) for p in patterns))
    else:
        return iter(chain.from_iterable(path.glob(p) for p in patterns))


def prune_excluded(
    files: Iterable[Path], exclude: Optional[Iterable[Union[str, PathLike]]]
) -> Iterable[Path]:
    if any(exclude):
        exclude = [Path(e).expanduser().absolute() for e in exclude]
    else:
        exclude = []
    for f in files:
        if any(f.samefile(e) or f.is_relative_to(e) for e in exclude):
            continue
        yield f


def set_logger(level):
    """setup custom logger"""
    logger = logging.getLogger("fprettify-logger")
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter(
        "%(levelname)s: File %(ffilename)s, line %(fline)s\n    %(message)s"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def show_diff(buffer, fname):
    i = open(fname).readlines()
    o = buffer.readlines()
    print("".join(unified_diff(i, o, fname, fname, n=5)), file=sys.stdout)


def diff(a, b, a_name, b_name):
    # type: (str, str, str, str) -> str

    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line + "\n" for line in a.splitlines()]
    b_lines = [line + "\n" for line in b.splitlines()]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )


def str2bool(str) -> Optional[bool]:
    """Convert the given string to a boolean."""
    if str.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif str.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return None


def log_message(message, level, filename, line_nr):
    """log a message"""

    logger = logging.getLogger("fprettify-logger")
    logger_d = {"ffilename": filename, "fline": line_nr}
    logger_to_use = getattr(logger, level)
    logger_to_use(message, extra=logger_d)


def log_exception(e, message):
    """log an exception and a message"""
    log_message(message, "exception", e.filename, e.line_nr)
