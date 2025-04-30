#!/bin/bash
set -e

cd /home/json
cd build
cmake ..  
cmake --build .
ctest
