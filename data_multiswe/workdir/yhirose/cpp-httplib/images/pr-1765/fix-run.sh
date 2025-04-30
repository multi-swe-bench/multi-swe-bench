#!/bin/bash
set -e

cd /home/cpp-httplib
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd test 
make

