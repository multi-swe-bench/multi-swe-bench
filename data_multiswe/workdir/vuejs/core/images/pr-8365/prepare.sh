#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e8bbe873e579f3d3a74c44af28f7df9e7a06978
bash /home/check_git_changes.sh

pnpm install || true

