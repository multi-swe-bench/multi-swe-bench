#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b4a3e019f8eeb3423065f7b24d790358e8cbc59
bash /home/check_git_changes.sh

