#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 64963dcbd6162c52ba9273bb55d78c7a442b12f4
bash /home/check_git_changes.sh

