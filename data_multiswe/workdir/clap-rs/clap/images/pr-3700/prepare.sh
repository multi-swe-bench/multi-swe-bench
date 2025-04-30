#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 55e791e80ed4167cb11d968546aabb96f6760029
bash /home/check_git_changes.sh

cargo test || true

