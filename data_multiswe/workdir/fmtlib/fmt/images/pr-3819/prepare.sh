#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 0147e08225db261f5689fc17a986ede7f1db56f0
bash /home/check_git_changes.sh
mkdir build || true

