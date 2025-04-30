#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 90c042eeaef36ef6a1718b19cc9ea213ac249f6e
bash /home/check_git_changes.sh

cargo test || true

