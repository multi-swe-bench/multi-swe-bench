#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 230441e1a594eea80d0f3384488925ddae074155
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

