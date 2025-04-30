#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3a4d947603603f5dea742442d32bc131e9786d25
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

