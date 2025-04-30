#!/bin/bash
set -e

cd /home/axios
git reset --hard
bash /home/check_git_changes.sh
git checkout 7fbfbbeff69904cd64e8ac62da8969a1e633ee23
bash /home/check_git_changes.sh

npm ci || true

