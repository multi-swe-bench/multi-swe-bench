#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5b73699825fddc805be58c2719503b114e00ea61
bash /home/check_git_changes.sh

cargo test || true

