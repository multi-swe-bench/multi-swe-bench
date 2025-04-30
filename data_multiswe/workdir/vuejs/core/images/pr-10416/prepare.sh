#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 89de26cdcdddef8096417ea494de113399629d5b
bash /home/check_git_changes.sh

pnpm install || true

