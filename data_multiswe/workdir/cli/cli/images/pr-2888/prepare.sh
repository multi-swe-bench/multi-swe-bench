#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7e8348a68f96c5983251f89871167797545dbbe0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

