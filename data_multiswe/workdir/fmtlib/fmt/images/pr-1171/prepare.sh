#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 87fbc6f7566e4d3266bd3a2cd69f6c90e1aefa5d
bash /home/check_git_changes.sh
mkdir build || true

