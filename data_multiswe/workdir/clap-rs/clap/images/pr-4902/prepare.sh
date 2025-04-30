#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout d597cf7bd6a1fc073ff483f3e39d09c3bd26f95c
bash /home/check_git_changes.sh

cargo test || true

