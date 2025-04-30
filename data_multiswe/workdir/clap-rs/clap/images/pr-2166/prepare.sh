#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d2ef79512121c7b79eecea150403eaa49f54c3a
bash /home/check_git_changes.sh

cargo test || true

