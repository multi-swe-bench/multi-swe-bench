#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout b6177f0459044a7e3fb882ecda9c80e44e4d95de
bash /home/check_git_changes.sh

cargo test || true

