#!/bin/bash
set -e

cd /home/zstd
git apply --whitespace=nowarn /home/test.patch
make 
make test

