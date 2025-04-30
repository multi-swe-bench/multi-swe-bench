#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d7d5a6b7530ea7b91f7b096f94892f417fd00f95
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

