#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 7c79e76f2f55b1aab083fa201a86bbc8c8c35711
bash /home/check_git_changes.sh

cargo test || true

