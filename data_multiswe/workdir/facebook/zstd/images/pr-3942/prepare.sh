#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 372fddf4e6a6db6776b745f31c02a7c8c8dfc83f
bash /home/check_git_changes.sh

