#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 135b15467eda2394b017f2a7d25cda1417c0feec
bash /home/check_git_changes.sh

cargo test || true

