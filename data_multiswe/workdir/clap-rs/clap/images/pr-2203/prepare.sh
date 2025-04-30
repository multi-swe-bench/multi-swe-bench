#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout be6e1f764763b0f0b4a5cbc497d745251307a4c4
bash /home/check_git_changes.sh

cargo test || true

