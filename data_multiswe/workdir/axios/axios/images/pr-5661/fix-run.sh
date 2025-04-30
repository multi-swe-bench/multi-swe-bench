#!/bin/bash
set -e

cd /home/axios
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
npm test -- --reporter console

