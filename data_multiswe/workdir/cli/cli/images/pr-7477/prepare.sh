#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f4038d9811284cda099151eec6d89f309c490f1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

