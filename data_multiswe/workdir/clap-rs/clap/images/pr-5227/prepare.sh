#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c81df6855dbb12d1f1e28c7894aab6cc892abf3
bash /home/check_git_changes.sh

cargo test || true

