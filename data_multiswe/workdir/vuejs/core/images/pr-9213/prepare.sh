#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout dadb3632a0f824f6e6a1c246ed8788bea5cbcad6
bash /home/check_git_changes.sh

pnpm install || true

