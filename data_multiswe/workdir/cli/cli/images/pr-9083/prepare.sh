#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 95a2f95f75f4b143699d87294788210ffb558248
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

