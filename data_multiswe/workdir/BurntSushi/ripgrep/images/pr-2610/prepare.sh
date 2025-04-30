#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 86ef6833085428c21ef1fb7f2de8e5e7f54f1f72
bash /home/check_git_changes.sh

cargo test || true

