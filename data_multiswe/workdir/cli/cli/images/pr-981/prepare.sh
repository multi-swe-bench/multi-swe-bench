#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4e73c83fd1a21b571ced2f12d723ad58055eb90b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

