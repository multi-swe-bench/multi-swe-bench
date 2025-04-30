#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 201842d75c20685b3f8cff3a708a61b34f228196
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

