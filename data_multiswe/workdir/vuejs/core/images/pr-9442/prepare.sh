#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 4162311efdb0db5ca458542e1604b19efa2fae0e
bash /home/check_git_changes.sh

pnpm install || true

