#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f80400a896ac10037090a6f7c78751adebd2e2c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

