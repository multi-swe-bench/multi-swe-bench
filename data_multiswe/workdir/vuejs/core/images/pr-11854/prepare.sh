#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout fe2ab1bbac7e29edd275350b3ca9bbb54285f598
bash /home/check_git_changes.sh

pnpm install || true

