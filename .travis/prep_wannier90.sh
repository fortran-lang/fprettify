#!/usr/bin/env bash
wget https://github.com/pseewald/wannier90/archive/fprettify-test.tar.gz
mkdir fortran_tests/before/wannier90 && tar -xf fprettify-test.tar.gz -C fortran_tests/before/wannier90 --strip-components=1
rm fprettify-test.tar.gz
