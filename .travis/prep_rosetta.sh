#!/usr/bin/env bash
wget https://github.com/pseewald/RosettaCodeData/archive/fprettify-test.tar.gz
mkdir fortran_tests/before/RosettaCodeData && tar -xf fprettify-test.tar.gz -C fortran_tests/before/RosettaCodeData --strip-components=1
rm fprettify-test.tar.gz
