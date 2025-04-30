#!/bin/bash
set -e

cd /home/dayjs
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
npm test -- --verbose && codecov 

