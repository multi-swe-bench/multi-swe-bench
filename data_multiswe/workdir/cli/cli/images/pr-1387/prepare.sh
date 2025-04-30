#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout eb1b9122d8d7984fc33656e5ef90bb5b2b29e9df
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

