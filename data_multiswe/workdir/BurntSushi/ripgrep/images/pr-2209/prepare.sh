#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 4dc6c73c5a9203c5a8a89ce2161feca542329812
bash /home/check_git_changes.sh

cargo test || true

