#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 272a3f347d97c48a97dcc68e689c48e5aa955b77
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

