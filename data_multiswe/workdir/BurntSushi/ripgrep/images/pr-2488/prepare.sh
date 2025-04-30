#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 041544853c86dde91c49983e5ddd0aa799bd2831
bash /home/check_git_changes.sh

cargo test || true

