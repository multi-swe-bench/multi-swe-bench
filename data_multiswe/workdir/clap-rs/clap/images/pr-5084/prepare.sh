#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 0a870087991b718495c94966f9c6e4c2dd425cc8
bash /home/check_git_changes.sh

cargo test || true

