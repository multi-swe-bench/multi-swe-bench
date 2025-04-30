#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 962791bf27e289949de19c4bfb14158e887b0bb6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

