#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout a9893458ec519aae442e1b99e64e6d74685cd22c
bash /home/check_git_changes.sh

pnpm install || true

