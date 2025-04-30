#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout ddd55e57dc4b0205e02c121f1116704bd1b51956
bash /home/check_git_changes.sh

cargo test || true

