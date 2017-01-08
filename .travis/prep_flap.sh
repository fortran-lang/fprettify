#!/usr/bin/env bash
wget https://github.com/szaghi/FLAP/archive/9e601.tar.gz
mkdir fortran_tests/before/FLAP && tar -xf 9e601.tar.gz -C fortran_tests/before/FLAP --strip-components=1
