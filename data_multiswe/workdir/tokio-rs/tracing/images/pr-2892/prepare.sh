#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e4a4bef5e4e8b7435e9e50e8bae25afba25d7d7
bash /home/check_git_changes.sh

cargo test || true

