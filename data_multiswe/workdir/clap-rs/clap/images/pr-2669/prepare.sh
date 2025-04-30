#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 10c7228b3f8f1e9e1f2b9744cd802d8658c36f1a
bash /home/check_git_changes.sh

cargo test || true

