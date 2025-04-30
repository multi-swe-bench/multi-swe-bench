#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout fe59f7720342b3d313fe11bd3c7490b0e10aef2c
bash /home/check_git_changes.sh

cargo test || true

