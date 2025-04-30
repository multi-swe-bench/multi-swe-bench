#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 4912fc2acc3a957723dd5644a6c6075873a8c4f2
bash /home/check_git_changes.sh

