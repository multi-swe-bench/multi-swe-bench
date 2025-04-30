#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 48345d6e4822b4c0ea00d5c1c075a6b5ac663acf
bash /home/check_git_changes.sh

cargo test || true

