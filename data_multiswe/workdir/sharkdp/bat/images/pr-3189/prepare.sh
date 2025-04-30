#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout f8c6e90647221d8a5142bc50c7ea972562f6cdcd
bash /home/check_git_changes.sh

cargo test || true

