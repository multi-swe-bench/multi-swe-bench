#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout c03f55ec3a0511611fa7f0537f858544a0ed03bd
bash /home/check_git_changes.sh
mkdir build || true

