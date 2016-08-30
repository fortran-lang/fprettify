
import sys
import unittest

try:
    # Use the old Python 2's StringIO if available since
    # the converter does not yield unicode strings (yet)
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import fprettify


class FPrettifyTestCase(unittest.TestCase):
    def setUp(self):
        # we have large files to compare, raise the limit
        self.maxDiff = None

    def test_example(self):
        """Test the conversion for the example input/output"""

        with open('examples/fortran_after.f90', 'r') as fh:
            expected_output = fh.read()

        with open('examples/fortran_before.f90', 'r') as infile:
            outfile = StringIO()

            fprettify.reformat_ffile(infile, outfile)

            self.assertMultiLineEqual(expected_output, outfile.getvalue())

if __name__ == '__main__':
    unittest.main(argv=sys.argv)

#  vim: set ts=4 sw=4 tw=0 :
