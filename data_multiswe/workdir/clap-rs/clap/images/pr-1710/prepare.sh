#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout c192f5effbb9655964630952e530255462174f44
bash /home/check_git_changes.sh

cargo test || true

