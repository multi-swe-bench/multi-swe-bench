#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 779b9c19d5c373d4d89ef3d758cf7469e9941c31
bash /home/check_git_changes.sh

cargo test || true

