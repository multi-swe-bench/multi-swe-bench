#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 2da492e4dc1eedf4f7d666ecb38158d2d8c6528f
bash /home/check_git_changes.sh

cargo test || true

