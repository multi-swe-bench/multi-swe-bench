#!/bin/bash
set -e

cd /home/ponyc
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
make
make test

    