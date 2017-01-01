#!/usr/bin/env bash
wget https://github.com/acmeism/RosettaCodeData/archive/bba7b.tar.gz
mkdir fortran_tests/before/RosettaCodeData && tar -xf bba7b.tar.gz -C fortran_tests/before/RosettaCodeData --strip-components=1
