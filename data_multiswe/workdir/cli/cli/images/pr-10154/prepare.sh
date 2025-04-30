#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6fe21d8f5224c5d8a58d210bd2bc70f5a008294c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

