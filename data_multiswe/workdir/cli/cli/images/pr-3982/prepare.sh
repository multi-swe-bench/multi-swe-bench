#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a6710ec5064995aadd18da5808c8c4ff41a8199c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

