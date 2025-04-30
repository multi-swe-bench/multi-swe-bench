#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e510650a98a528d3c016cfdfddbe67ae3a470a5
bash /home/check_git_changes.sh

cargo test || true

