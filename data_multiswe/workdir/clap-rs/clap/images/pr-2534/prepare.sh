#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 33c305ea6ff6cdda7796e57966374cb40633968f
bash /home/check_git_changes.sh

cargo test || true

