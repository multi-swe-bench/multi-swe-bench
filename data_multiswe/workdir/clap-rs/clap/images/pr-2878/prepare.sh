#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 089c4160cf371f95ea0aed0997edfb018aeff8ce
bash /home/check_git_changes.sh

cargo test || true

