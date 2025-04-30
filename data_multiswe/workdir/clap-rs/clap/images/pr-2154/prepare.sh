#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 6ce1e4fda211a7373ce7c4167964e6ca073bdfc1
bash /home/check_git_changes.sh

cargo test || true

