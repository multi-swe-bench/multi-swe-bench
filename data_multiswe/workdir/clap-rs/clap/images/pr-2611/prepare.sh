#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 610d56d1c63042359d6181c89572e894274f4ae7
bash /home/check_git_changes.sh

cargo test || true

