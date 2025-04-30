#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 90a74044ee03963f9d4c4453ce651dc907bc94d4
bash /home/check_git_changes.sh

cargo test || true

