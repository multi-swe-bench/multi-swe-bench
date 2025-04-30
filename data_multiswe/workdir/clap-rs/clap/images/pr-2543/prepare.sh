#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 947523f7f5c25579affa3f8c0499ff362d523611
bash /home/check_git_changes.sh

cargo test || true

