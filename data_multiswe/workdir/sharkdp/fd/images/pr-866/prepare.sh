#!/bin/bash
set -e

cd /home/fd
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b5b3ec47b98984121e2665c7bad5274cb8db796
bash /home/check_git_changes.sh

cargo test || true

