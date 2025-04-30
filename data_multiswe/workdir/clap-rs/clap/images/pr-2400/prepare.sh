#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 42c03775b538425d0365a02ae58dcb36390070ae
bash /home/check_git_changes.sh

cargo test || true

