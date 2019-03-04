#!/usr/bin/env bash
wget https://github.com/pseewald/cp2k/archive/fprettify-test.tar.gz
mkdir fortran_tests/before/cp2k
tar -xf fprettify-test.tar.gz -C fortran_tests/before/cp2k --strip-components=1 cp2k-fprettify-test/src
rm fprettify-test.tar.gz
