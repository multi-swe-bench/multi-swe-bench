#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2f94adabb2ddbda4cfbb717019714dca6f0a3fa1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

