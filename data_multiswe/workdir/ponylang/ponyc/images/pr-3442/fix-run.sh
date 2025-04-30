#!/bin/bash
set -e

cd /home/ponyc
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
make -f Makefile-lib-llvm
make -f Makefile-lib-llvm test

    