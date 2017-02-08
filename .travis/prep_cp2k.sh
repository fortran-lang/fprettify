#!/usr/bin/env bash
wget https://github.com/pseewald/cp2k/archive/fprettify-test.tar.gz
tar -xf fprettify-test.tar.gz -C fortran_tests/before --strip-components=1 cp2k-fprettify-test/cp2k/src
rm fprettify-test.tar.gz
