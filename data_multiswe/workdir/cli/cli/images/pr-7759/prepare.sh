#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b9cacbc3474ffd6442a203fe2c5d11f6fe89050c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

