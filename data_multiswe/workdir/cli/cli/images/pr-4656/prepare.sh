#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7ef3abe48f97116e9f1e5228c7f0982cefe3fd64
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

