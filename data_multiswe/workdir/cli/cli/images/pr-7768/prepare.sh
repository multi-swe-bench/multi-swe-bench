#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 885ccd7424acb8db9519dc972bbac2b67c5a9d3f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

