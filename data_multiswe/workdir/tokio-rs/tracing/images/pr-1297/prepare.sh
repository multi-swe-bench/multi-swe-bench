#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout ba57971f2c424b89338e39a5443575fd78b09bb6
bash /home/check_git_changes.sh

cargo test || true

