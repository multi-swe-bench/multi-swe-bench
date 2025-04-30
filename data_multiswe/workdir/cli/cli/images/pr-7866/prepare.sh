#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fd7f987e581b8e49dcdcdad266db30a29e9fb41d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

