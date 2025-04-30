#!/bin/bash
set -e

cd /home/core
pnpm run test-unit --no-watch --reporter=verbose

