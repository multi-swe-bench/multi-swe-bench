#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout 3af35492320077b2abf7cc70117ea02aa24389a3
bash /home/check_git_changes.sh

cargo test || true

