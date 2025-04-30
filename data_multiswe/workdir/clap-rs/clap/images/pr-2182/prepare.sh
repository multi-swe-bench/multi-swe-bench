#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout fad3d9632ebde36004455084df2c9052afe40855
bash /home/check_git_changes.sh

cargo test || true

