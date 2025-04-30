#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 30066b0042d0c5928d959e288144300cb28196c9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

