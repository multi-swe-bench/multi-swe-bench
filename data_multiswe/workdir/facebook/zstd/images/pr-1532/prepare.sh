#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout eb3a7a38270dc2a1f533c1b347f8b9b56e789f8f
bash /home/check_git_changes.sh

