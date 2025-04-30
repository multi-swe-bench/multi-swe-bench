#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 75e02b5099a08166bdf407127916734c48209ee9
bash /home/check_git_changes.sh

pnpm install || true

