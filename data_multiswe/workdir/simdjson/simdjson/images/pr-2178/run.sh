#!/bin/bash
set -e

cd /home/simdjson
cd build
cmake -DSIMDJSON_DEVELOPER_MODE=ON ..
cmake --build .
ctest
