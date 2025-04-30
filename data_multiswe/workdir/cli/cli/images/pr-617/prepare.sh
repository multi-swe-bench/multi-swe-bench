#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 115b4b5ee9c0eb1598c23842f6fd2def124ec421
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

