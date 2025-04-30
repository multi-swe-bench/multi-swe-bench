#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout d6eede9e085f0b36edcf0a2f6dff5f7875181019
bash /home/check_git_changes.sh
mkdir build || true

