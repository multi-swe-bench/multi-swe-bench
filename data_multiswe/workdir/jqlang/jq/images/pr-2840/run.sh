#!/bin/bash
set -e

cd /home/jq
autoreconf -i
./configure --with-oniguruma=builtin
make clean                     
make -j8
make check
