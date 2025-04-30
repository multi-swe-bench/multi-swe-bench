#!/bin/bash
set -e

cd /home/dayjs
git apply --whitespace=nowarn /home/test.patch
npm test -- --verbose && codecov 

