#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ca62aa18559d8c30056d6c1ebfda2840e0a322c
bash /home/check_git_changes.sh

cargo test || true

