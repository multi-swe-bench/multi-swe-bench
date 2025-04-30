#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 363dacbbed8cc9f86026ec1b1e38c6dca0d78c08
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

