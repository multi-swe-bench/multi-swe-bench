#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 2bab4a22494e3f10da0b708da7a1eebaa483b727
bash /home/check_git_changes.sh

cargo test || true

