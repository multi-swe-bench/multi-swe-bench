#!/bin/bash
set -e

cd /home/ponyc
make -f Makefile-lib-llvm
make -f Makefile-lib-llvm test
    