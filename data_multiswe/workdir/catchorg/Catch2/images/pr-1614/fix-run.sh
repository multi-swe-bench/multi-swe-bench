#!/bin/bash
set -e

cd /home/Catch2
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest

