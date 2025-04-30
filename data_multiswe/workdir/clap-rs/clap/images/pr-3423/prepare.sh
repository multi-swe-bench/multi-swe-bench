#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout edf9d057c4df1a5cbd35fc18580fc535d1f7cd75
bash /home/check_git_changes.sh

cargo test || true

