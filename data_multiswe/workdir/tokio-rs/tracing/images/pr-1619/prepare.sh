#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 7dda7f5e90a649aee36eaa51c11b59f62470d456
bash /home/check_git_changes.sh

cargo test || true

