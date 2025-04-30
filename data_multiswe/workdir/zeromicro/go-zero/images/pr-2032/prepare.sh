#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 93b3f5030fbf5cad686d552ab22b0d2506124a44
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

