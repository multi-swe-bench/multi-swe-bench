#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout d0b513eb463f580e29378e43d112ff6859aa366e
bash /home/check_git_changes.sh

pnpm install || true

