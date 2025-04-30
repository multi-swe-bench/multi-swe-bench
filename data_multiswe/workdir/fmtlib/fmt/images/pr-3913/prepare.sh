#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b5f3de3b57505c7f1a60ee40ef3448c623b1326
bash /home/check_git_changes.sh
mkdir build || true

