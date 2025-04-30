#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout e26fd7b1d15cb3335a4c2230cc49b1008daddca1
bash /home/check_git_changes.sh

pnpm install || true

