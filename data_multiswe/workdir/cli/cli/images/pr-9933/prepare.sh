#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9177b22a213318ccc00a9b08fbac1dd14fb3a839
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

