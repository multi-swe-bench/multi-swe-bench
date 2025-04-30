#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 0eccd556ac694cdb68251f758e9b80574be349a8
bash /home/check_git_changes.sh

cargo test || true

