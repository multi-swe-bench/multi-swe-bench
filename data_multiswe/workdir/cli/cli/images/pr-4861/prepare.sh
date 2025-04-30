#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 43ae0e5f87e48253f7dfe6deb0655142b8800b43
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

