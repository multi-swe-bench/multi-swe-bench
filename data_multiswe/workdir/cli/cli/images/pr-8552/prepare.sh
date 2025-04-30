#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 57f6787c154d56d3c5461afed619e36b8a8394ec
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

