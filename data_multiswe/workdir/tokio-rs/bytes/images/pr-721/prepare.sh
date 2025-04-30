#!/bin/bash
set -e

cd /home/bytes
git reset --hard
bash /home/check_git_changes.sh
git checkout 9965a04b5684079bb614addd750340ffc165a9f5
bash /home/check_git_changes.sh

cargo test || true

