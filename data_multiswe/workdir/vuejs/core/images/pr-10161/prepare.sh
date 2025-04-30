#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout f1068fc60ca511f68ff0aaedcc18b39124791d29
bash /home/check_git_changes.sh

pnpm install || true

