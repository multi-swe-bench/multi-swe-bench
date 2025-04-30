#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 530d9ec5f69a39246314183d942d37986c01dc46
bash /home/check_git_changes.sh

pnpm install || true

