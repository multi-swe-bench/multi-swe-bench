#!/bin/bash
set -e

cd /home/axios
git apply --whitespace=nowarn /home/test.patch
npm test -- --reporter console

