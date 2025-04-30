#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 1408f1824d6a23643e178ee6e46478fb550a0963
bash /home/check_git_changes.sh
mkdir build || true

