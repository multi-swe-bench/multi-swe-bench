#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a6df0d39b7325929702c81aa87fe01c9f4143a6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

