#!/bin/bash
set -e

cd /home/core
git apply /home/test.patch /home/fix.patch
pnpm run test-unit --no-watch --reporter=verbose

