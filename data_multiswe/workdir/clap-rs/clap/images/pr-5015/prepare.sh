#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout c2191674b049d8ded04db262454c3f6ae6a0c724
bash /home/check_git_changes.sh

cargo test || true

