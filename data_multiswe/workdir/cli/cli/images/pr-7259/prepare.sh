#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout dbc2f05124e7cbc7648967a5f9df7dbb448ce31c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

