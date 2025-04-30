#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2d0d86f7e7f71c0919b7b38acabf1d24f6b8279c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

