#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 88cae9f5be67989be191cd4a1fe043ddbeafe629
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

