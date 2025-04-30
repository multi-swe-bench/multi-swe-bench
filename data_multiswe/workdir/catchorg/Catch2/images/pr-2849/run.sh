#!/bin/bash
set -e

cd /home/Catch2
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest
