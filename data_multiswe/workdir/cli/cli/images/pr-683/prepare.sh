#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout bc3f964621054e9478257a47cea87c6a475dde90
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

