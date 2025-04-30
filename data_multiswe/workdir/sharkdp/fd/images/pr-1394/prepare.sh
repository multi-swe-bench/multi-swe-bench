#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 93cdb2628e89dd5831eee22b8df697aea00eca3b
bash /home/check_git_changes.sh

cargo test || true

