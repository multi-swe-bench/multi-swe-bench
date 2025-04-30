#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 441ff68c2d63536f0e2fd7e171d6fa7d76b2f4c3
bash /home/check_git_changes.sh

cargo test || true

