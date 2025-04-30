#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout d298c431cc422b53cf4e9c69bf1daf926c33b6e0
bash /home/check_git_changes.sh

pnpm install || true

