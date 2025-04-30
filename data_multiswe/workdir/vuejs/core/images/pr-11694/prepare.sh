#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout fbc0c42bcf6dea5a6ae664223fa19d4375ca39f0
bash /home/check_git_changes.sh

pnpm install || true

