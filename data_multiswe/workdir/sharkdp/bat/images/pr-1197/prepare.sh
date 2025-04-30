#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout 2b82203041e0a4242659b95a4fa2ae6454497637
bash /home/check_git_changes.sh

cargo test || true

