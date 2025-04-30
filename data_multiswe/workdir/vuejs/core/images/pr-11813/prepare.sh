#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b6bc2374d93e5f76d9266a0fcc5c10a8cafef5b
bash /home/check_git_changes.sh

pnpm install || true

