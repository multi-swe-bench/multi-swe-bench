#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 634519720a21fb5a6871454e1cadad7053a568b8
bash /home/check_git_changes.sh

pnpm install || true

