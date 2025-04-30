#!/bin/bash
set -e

cd /home/simdjson
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build
cmake -DSIMDJSON_DEVELOPER_MODE=ON ..
cmake --build .
ctest

