#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c2ee024a215dc149baeb3a81755216636eddd64
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

