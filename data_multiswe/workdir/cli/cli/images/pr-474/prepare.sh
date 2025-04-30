#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 55b66feb423019879fa1ce6a7718a79b6b7ff0c0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

