#!/bin/bash
set -e

cd /home/bytes
git reset --hard
bash /home/check_git_changes.sh
git checkout 068ed41bc02c21fe0a0a4d8e95af8a4668276f5d
bash /home/check_git_changes.sh

cargo test || true

