#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c581a093ed5b61ae67e2907931159dfc28b4dc67
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

