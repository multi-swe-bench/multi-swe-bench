#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 6e1e824473e15eba246e1c43704c5d88fa237a17
bash /home/check_git_changes.sh

cargo test || true

