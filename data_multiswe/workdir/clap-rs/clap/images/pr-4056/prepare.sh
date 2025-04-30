#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 0129d99f4c4208e78a770657dc3d628a3bba8f19
bash /home/check_git_changes.sh

cargo test || true

