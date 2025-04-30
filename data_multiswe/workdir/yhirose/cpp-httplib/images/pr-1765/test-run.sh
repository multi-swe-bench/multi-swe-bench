#!/bin/bash
set -e

cd /home/cpp-httplib
git apply --whitespace=nowarn /home/test.patch
cd test 
make

