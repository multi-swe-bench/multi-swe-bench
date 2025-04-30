#!/bin/bash
set -e

cd /home/simdjson
git apply --whitespace=nowarn /home/test.patch
cd build
cmake -DSIMDJSON_DEVELOPER_MODE=ON ..
cmake --build .
ctest

