#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ca25026613e7b6b19b77d23b31e9fad25492fe29
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

