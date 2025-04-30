#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 835b910e7d758efdfdce9f23df1b190deb3373db
bash /home/check_git_changes.sh
mkdir build || true

