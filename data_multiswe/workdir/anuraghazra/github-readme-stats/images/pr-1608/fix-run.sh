#!/bin/bash
set -e

cd /home/github-readme-stats
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
npm run test -- --verbose

