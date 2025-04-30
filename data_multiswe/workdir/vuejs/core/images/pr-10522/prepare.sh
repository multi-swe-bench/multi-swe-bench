#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout caeb8a68811a1b0f799632582289fcf169fb673c
bash /home/check_git_changes.sh

pnpm install || true

