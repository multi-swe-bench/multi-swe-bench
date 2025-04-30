#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9b7ee3acefe9cfc5a247bdcda8c15f2d06abf049
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

