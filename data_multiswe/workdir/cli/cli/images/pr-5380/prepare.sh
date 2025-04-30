#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8dbd07212c239d32675d277363cc1f492ab62ad0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

