#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 020851e57d9a9f727c6ea07e9c1575430af02b73
bash /home/check_git_changes.sh

pnpm install || true

