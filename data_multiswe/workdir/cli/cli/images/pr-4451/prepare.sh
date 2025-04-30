#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7abf682e26d4619c9639e6b1ece8d5b810e0bf04
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

