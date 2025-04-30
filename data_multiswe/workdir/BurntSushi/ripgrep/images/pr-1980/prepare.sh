#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 9b01a8f9ae53ebcd05c27ec21843758c2c1e823f
bash /home/check_git_changes.sh

cargo test || true

