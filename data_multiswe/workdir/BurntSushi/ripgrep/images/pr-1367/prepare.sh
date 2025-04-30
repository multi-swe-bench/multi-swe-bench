#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 4858267f3b97fe2823d2ce104c1f90ec93eee8d7
bash /home/check_git_changes.sh

cargo test || true

