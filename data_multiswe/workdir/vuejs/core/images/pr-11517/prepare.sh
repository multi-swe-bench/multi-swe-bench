#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout b74687c0bbc0083513a1f5da3a2995cfb5f48246
bash /home/check_git_changes.sh

pnpm install || true

