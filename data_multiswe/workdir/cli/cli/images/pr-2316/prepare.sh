#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e89036d49993087b9b45060cc1292a18e1d853a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

