#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout 33128d75f22a7c029df17b1ee595865933551469
bash /home/check_git_changes.sh

cargo test || true

