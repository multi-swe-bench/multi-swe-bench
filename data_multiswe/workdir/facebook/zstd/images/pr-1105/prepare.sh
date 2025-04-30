#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 04212178b50131ecbbf7bc2ffcce4d5ddcfd8e11
bash /home/check_git_changes.sh

