#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d871da679b237397dc9a4df2aa9073cf46f686db
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

