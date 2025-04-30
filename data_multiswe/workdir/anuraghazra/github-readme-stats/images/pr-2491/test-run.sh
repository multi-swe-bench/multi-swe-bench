#!/bin/bash
set -e

cd /home/github-readme-stats
git apply --whitespace=nowarn /home/test.patch
npm run test -- --verbose

