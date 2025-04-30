#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 514f28bc92ed683d53292cbe9457db3ec5df7b6f
bash /home/check_git_changes.sh

cargo test || true

