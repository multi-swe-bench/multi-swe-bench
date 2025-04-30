#!/bin/bash
set -e

cd /home/fmt
git apply --whitespace=nowarn /home/test.patch
cd build
cmake ..  
cmake --build .
ctest

