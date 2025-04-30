#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 58b0529d13c52882b0a9668db17aa92769e40896
bash /home/check_git_changes.sh

cargo test || true

