#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 823a28a1f4cb89be7ec22ee5d34754b54e9f2b6e
bash /home/check_git_changes.sh

