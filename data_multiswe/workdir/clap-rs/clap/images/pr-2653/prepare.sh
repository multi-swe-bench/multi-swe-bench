#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 4bec66dd03640a26df2d05dc89828f6f97da113a
bash /home/check_git_changes.sh

cargo test || true

