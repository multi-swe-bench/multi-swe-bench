#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 055568d3fe9fd3e96366035e4129975001c7e01c
bash /home/check_git_changes.sh

cargo test || true

