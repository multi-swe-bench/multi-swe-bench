#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a8f57676749c123effdcc1783b4ffe4a3d14fd2a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

