#!/bin/bash
set -e

cd /home/jq
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
autoreconf -i
./configure --with-oniguruma=builtin
make clean                     
make -j8
make check

