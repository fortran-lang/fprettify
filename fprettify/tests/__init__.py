from __future__ import print_function
import sys
import os
import unittest
import hashlib
import logging

import fprettify

class FPrettifyTestCase(unittest.TestCase):
    def setUp(self):
        self.orig_dir = r'examples/before/'
        self.fpr_dir = r'examples/after/'
        self.hashdir = r'examples/test_checksums/'
        self.hashfile = os.path.join(self.hashdir, 'sha256_hash')
        self.fortran_extension = [".f90", ".F", ".f"]

        fprettify.set_fprettify_logger(logging.INFO)


        if not os.path.exists(self.orig_dir):
            os.makedirs(self.orig_dir)
        if not os.path.exists(self.fpr_dir):
            os.makedirs(self.fpr_dir)
        if not os.path.exists(self.hashdir):
            os.makedirs(self.hashdir)
        if not os.path.exists(self.hashfile):
            open(self.hashfile, 'w').close()

    def test_examples(self):
        """test fprettify output for all fortran files in examples directory against tabulated checksums.
        """

        print('')
        sep_str = ' : '

        for dirpath, dirnames, filenames in os.walk(self.orig_dir):
            for example in [f for f in filenames if any([f.endswith(_) for _ in self.fortran_extension])]:
                print(os.path.join(dirpath, example), end=" ")
                sys.stdout.flush()

                dirpath_fpr = dirpath.replace(self.orig_dir, self.fpr_dir, 1)
                if not os.path.exists(dirpath_fpr):
                    os.makedirs(dirpath_fpr)

                with open(os.path.join(dirpath, example), 'r') as infile:

                    with open(os.path.join(dirpath_fpr, example), 'w') as outfile:
                        fprettify.reformat_ffile(infile, outfile)

                    m = hashlib.sha256()
                    with open(os.path.join(dirpath_fpr, example), 'r') as outfile:
                        m.update(outfile.read().encode('utf-8'))
                    test_line = os.path.join(dirpath, example).replace(self.orig_dir,"") + sep_str + m.hexdigest()
                    test_content = test_line.strip().split(sep_str)

                with open(self.hashfile, 'r') as fpr_hash:
                    found = False
                    for line in fpr_hash:
                        line_content = line.strip().split(sep_str)
                        if line_content[0] == test_content[0]:
                            found = True
                            self.assertEqual(line_content[1], test_content[1])
                            print("ok")
                            break

                if not found:
                    print("new")
                    with open(self.hashfile, 'a') as fpr_hash:
                        fpr_hash.write(test_line+'\n')

if __name__ == '__main__':
    unittest.main(argv=sys.argv)
