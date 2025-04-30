#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout ca3e14ca2d705fd9a7a05c868ea9139849027588
bash /home/check_git_changes.sh

cargo test || true

