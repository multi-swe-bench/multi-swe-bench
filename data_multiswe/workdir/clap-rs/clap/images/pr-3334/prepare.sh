#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout afd0342a9b092eb5bf3d4ce165b8a6a5c5f8328b
bash /home/check_git_changes.sh

cargo test || true

