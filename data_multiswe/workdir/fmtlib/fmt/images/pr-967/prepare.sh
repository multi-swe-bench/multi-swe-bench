#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout bf1f1c73e39c7ee6581ee0d5bb2471856a14bdb2
bash /home/check_git_changes.sh
mkdir build || true

