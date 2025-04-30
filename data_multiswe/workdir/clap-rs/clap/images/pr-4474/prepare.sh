#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 4d69e56f06d66ff5215a900dc42809d34a2d4184
bash /home/check_git_changes.sh

cargo test || true

