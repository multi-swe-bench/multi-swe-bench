#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b2397811400a6bc5d98f9e66cd95d34c377bb0e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

