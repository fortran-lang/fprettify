#!/usr/bin/env bash
wget https://github.com/pseewald/FLAP/archive/fprettify-test.tar.gz
mkdir fortran_tests/before/FLAP && tar -xf fprettify-test.tar.gz -C fortran_tests/before/FLAP --strip-components=1
rm fprettify-test.tar.gz
