#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout ffd4c9ccba0ffc74270a8d3ae75f11a7ba7a1a64
bash /home/check_git_changes.sh

cargo test || true

