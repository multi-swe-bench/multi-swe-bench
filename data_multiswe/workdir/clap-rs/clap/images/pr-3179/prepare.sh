#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 56ed9981da3a28205efa03a0e4f162359bab1dfe
bash /home/check_git_changes.sh

cargo test || true

