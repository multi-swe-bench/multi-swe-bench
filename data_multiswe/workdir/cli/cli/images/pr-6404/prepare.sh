#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a493f6dbe888b43625aaa8b2c7e01ca6445da1b2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

