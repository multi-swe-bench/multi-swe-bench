#!/bin/bash
set -e

cd /home/core
git apply /home/test.patch
pnpm run test-unit --no-watch --reporter=verbose

