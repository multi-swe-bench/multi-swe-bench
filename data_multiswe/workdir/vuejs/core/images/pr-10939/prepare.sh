#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 107e6143e716986269fc7c1d96733cb59dfadc53
bash /home/check_git_changes.sh

pnpm install || true

