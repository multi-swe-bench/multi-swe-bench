#!/bin/bash
set -e

cd /home/fmt
cd build
cmake ..  
cmake --build .
ctest
