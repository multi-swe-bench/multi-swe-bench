#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 179faa6bb249c3b8b80d933241759a6180324cbb
bash /home/check_git_changes.sh

cargo test || true

