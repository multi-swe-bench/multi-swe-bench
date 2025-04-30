#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 495e49e1a70989f4c8904c355f90d6149f673ce2
bash /home/check_git_changes.sh

cargo test || true

