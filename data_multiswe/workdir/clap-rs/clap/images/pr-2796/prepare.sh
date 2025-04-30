#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 236cf584cfeccdae995d19a25245d261e00c32e3
bash /home/check_git_changes.sh

cargo test || true

