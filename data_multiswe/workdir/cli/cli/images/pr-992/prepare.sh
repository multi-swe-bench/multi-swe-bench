#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 658d548c5e690b4fb4dd6ac06d4b798238b6157f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

