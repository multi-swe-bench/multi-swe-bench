#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout bc13c6de390751ecf8daa1b1ce8f775d104fdc65
bash /home/check_git_changes.sh
mkdir build || true

