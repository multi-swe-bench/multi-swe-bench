#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 76782744648658e1eee9ee8a666f01d554ac9a16
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

