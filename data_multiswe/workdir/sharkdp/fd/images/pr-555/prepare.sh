#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout ee673c92d375d9e5a6c126480a0383bbe3042b96
bash /home/check_git_changes.sh

cargo test || true

