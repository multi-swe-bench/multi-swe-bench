#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7e7735d450827faf2cf317130bfbcaa76d43b811
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

