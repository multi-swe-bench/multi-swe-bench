#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout c029771247e31bfba61fd62400986c0d155ef0d0
bash /home/check_git_changes.sh

cargo test || true

