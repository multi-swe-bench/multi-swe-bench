#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout f44c3b37d446d5f8e34539029dae0d806b25bb47
bash /home/check_git_changes.sh

pnpm install || true

