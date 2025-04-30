#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 5417c89387b67c3192ae9043473b556cd669ee15
bash /home/check_git_changes.sh

cargo test || true

