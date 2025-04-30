#!/bin/bash
set -e

cd /home/express
git apply --whitespace=nowarn /home/test.patch
npm run test-ci -- --reporter json 

