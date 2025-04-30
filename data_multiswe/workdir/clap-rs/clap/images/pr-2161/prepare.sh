#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f90f3e4bb09cc596aa10243fc1791fc574a5d0e
bash /home/check_git_changes.sh

cargo test || true

