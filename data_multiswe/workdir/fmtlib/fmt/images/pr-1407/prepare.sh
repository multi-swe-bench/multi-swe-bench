#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f918159edded99c9c0cf005c96ecc12e4cc92b1
bash /home/check_git_changes.sh
mkdir build || true

