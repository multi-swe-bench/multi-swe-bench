#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout d7d0371e74707ee601020f67de88e091cdae2673
bash /home/check_git_changes.sh

pnpm install || true

