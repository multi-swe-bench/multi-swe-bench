#!/bin/bash
set -e

cd /home/fmt
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build
cmake ..  
cmake --build .
ctest

