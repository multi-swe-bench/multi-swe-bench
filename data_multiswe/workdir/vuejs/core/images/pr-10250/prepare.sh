#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout d276a4f3e914aaccc291f7b2513e5d978919d0f9
bash /home/check_git_changes.sh

pnpm install || true

