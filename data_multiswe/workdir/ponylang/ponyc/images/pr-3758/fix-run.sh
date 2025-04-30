#!/bin/bash
set -e

cd /home/ponyc
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
make libs
make configure config=debug
make build config=debug
make test config=debug

