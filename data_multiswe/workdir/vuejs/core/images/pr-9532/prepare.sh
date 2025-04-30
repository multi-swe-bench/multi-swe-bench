#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout a93bcc4e29be0db6c310f717db3687feb3e4287c
bash /home/check_git_changes.sh

pnpm install || true

