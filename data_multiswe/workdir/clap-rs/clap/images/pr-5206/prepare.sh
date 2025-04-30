#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3383242b475c7e8f5e775ecfabdaf7ec5b70a686
bash /home/check_git_changes.sh

cargo test || true

