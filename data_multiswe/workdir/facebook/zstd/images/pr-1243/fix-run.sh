#!/bin/bash
set -e

cd /home/zstd
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
make 
make test

